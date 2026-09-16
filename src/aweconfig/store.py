"""keys.env storage: parse, edit, and atomically write the shell-env vault.

The vault is a plain shell file of `export NAME='value'` lines plus free-form
comments. Any POSIX shell can `source` it directly — the CLI is only a safe
editor on top, never a runtime dependency.
"""

from __future__ import annotations

import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path

NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
EXPORT_RE = re.compile(r"^export ([A-Za-z_][A-Za-z0-9_]*)=(.*)$")

DEFAULT_PATH = Path("~/.config/awe/keys.env")
HEADER = "# aweconfig vault - plain shell env file; keep mode 0600 and never commit it."


def keys_path() -> Path:
    """Vault location: $AWECONFIG_FILE if set, else ~/.config/awe/keys.env."""
    override = os.environ.get("AWECONFIG_FILE")
    return Path(override).expanduser() if override else DEFAULT_PATH.expanduser()


@dataclass
class Entry:
    name: str
    value: str


def valid_name(name: str) -> bool:
    return bool(NAME_RE.match(name))


def quote(value: str) -> str:
    """Single-quote for shell; embedded quotes use the '\\'' idiom."""
    return "'" + value.replace("'", "'\\''") + "'"


def unquote(raw: str) -> str:
    if len(raw) >= 2 and raw[0] == "'" and raw[-1] == "'":
        return raw[1:-1].replace("'\\''", "'")
    if len(raw) >= 2 and raw[0] == '"' and raw[-1] == '"':
        return _unquote_double(raw[1:-1])
    return raw


def _unquote_double(body: str) -> str:
    out = []
    i = 0
    while i < len(body):
        ch = body[i]
        if ch == "\\" and i + 1 < len(body) and body[i + 1] in '$"`\\':
            out.append(body[i + 1])
            i += 2
        else:
            out.append(ch)
            i += 1
    return "".join(out)


def parse_export(line: str) -> Entry | None:
    match = EXPORT_RE.match(line.strip())
    if not match:
        return None
    return Entry(match.group(1), unquote(match.group(2).strip()))


def read_lines(path: Path) -> list[str]:
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return []


def read_entries(path: Path) -> list[Entry]:
    return [entry for entry in (parse_export(l) for l in read_lines(path)) if entry]


def write_atomic(path: Path, lines: list[str]) -> None:
    """Write via temp file + rename so a crash never truncates the vault."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    os.chmod(tmp_name, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
    os.replace(tmp_name, path)


def init_file(path: Path) -> str:
    """Create the vault if missing; always (re)assert mode 0600. Idempotent."""
    if path.exists():
        os.chmod(path, 0o600)
        return "exists"
    write_atomic(path, [HEADER])
    return "created"


def set_entry(path: Path, name: str, value: str) -> bool:
    """Insert or replace one export. Returns True when a line was replaced."""
    lines = read_lines(path) or [HEADER]
    replaced = False
    out = []
    for line in lines:
        entry = parse_export(line)
        if entry is not None and entry.name == name:
            out.append(f"export {name}={quote(value)}")
            replaced = True
        else:
            out.append(line)
    if not replaced:
        if out and out[-1].strip():
            out.append("")
        out.append(f"export {name}={quote(value)}")
    write_atomic(path, out)
    return replaced


def remove_entry(path: Path, name: str) -> bool:
    """Drop one export line. Returns True when it was there."""
    lines = read_lines(path)
    out = [line for line in lines if not _is_named_export(line, name)]
    if len(out) == len(lines):
        return False
    write_atomic(path, out)
    return True


def _is_named_export(line: str, name: str) -> bool:
    entry = parse_export(line)
    return entry is not None and entry.name == name


def mask(value: str) -> str:
    if len(value) >= 14:
        return value[:6] + "..." + value[-4:]
    if len(value) > 4:
        return value[:2] + "..."
    return "..."
