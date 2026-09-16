"""One-way migration of secret exports from a shell rc file into the vault.

A "paragraph" is a run of non-blank lines. A paragraph moves only when every
export in it looks like a secret (name contains TOKEN/KEY/SECRET, or was named
explicitly). Comment lines ride along with their paragraph, so `## Anthropic`
style section headers survive the move. Mixed paragraphs stay put — the
dry-run report names them so the user can pass --name to force them through.
"""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from .store import Entry, parse_export, quote, read_entries, read_lines, write_atomic

SECRET_NAME_RE = re.compile(r"TOKEN|KEY|SECRET")


def is_secret_name(name: str, extra_names: tuple[str, ...] = ()) -> bool:
    return bool(SECRET_NAME_RE.search(name)) or name in extra_names


@dataclass
class ImportPlan:
    move_paragraphs: list[list[str]] = field(default_factory=list)
    moved: list[Entry] = field(default_factory=list)
    kept: list[str] = field(default_factory=list)
    insert_at: int | None = None
    source_line: str = ""

    @property
    def moved_names(self) -> list[str]:
        return [entry.name for entry in self.moved]


@dataclass
class ImportResult:
    plan: ImportPlan
    backup_path: Path | None = None
    skipped_dupes: list[str] = field(default_factory=list)


def _paragraph_ranges(lines: list[str]) -> list[tuple[int, int]]:
    ranges = []
    start = None
    for index, line in enumerate(lines):
        if line.strip():
            if start is None:
                start = index
        elif start is not None:
            ranges.append((start, index))
            start = None
    if start is not None:
        ranges.append((start, len(lines)))
    return ranges


def plan_import(
    zshrc_text: str, extra_names: tuple[str, ...] = (), source_line: str = ""
) -> ImportPlan | None:
    """Decide what would move. Returns None when nothing qualifies."""
    lines = zshrc_text.splitlines()
    plan = ImportPlan(source_line=source_line)
    drop: set[int] = set()
    for start, end in _paragraph_ranges(lines):
        paragraph = lines[start:end]
        entries = [entry for entry in (parse_export(l) for l in paragraph) if entry]
        if entries and all(is_secret_name(e.name, extra_names) for e in entries):
            plan.move_paragraphs.append(paragraph)
            plan.moved.extend(entries)
            drop.update(range(start, end))
            if plan.insert_at is None:
                plan.insert_at = start
        else:
            plan.kept.extend(entry.name for entry in entries)
    if not plan.moved:
        return None
    return plan


def rebuild_rc(lines: list[str], plan: ImportPlan, has_source_line: bool) -> str:
    """Original file minus moved paragraphs, plus one source line where they were."""
    drop: set[int] = set()
    search_from = 0
    for paragraph in plan.move_paragraphs:
        size = len(paragraph)
        for index in range(search_from, len(lines) - size + 1):
            if lines[index:index + size] == paragraph:
                drop.update(range(index, index + size))
                search_from = index + size
                break
    out = []
    for index, line in enumerate(lines):
        if index == plan.insert_at and not has_source_line and plan.source_line:
            out.append(plan.source_line)
            out.append("")
        if index not in drop:
            out.append(line)
    return "\n".join(out) + "\n"


def apply_import(plan: ImportPlan, rc_path: Path, vault: Path) -> ImportResult:
    """Backup the rc file, rewrite it, and append the moved keys to the vault."""
    backup_path = rc_path.with_name(
        rc_path.name + ".bak-" + datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    )
    shutil.copy2(rc_path, backup_path)

    original_lines = read_lines(rc_path)
    has_source_line = bool(plan.source_line) and plan.source_line in original_lines
    rc_path.write_text(rebuild_rc(original_lines, plan, has_source_line), encoding="utf-8")

    existing = {entry.name for entry in read_entries(vault)}
    vault_lines = read_lines(vault)
    skipped_dupes: list[str] = []
    appended_any = False
    for paragraph in plan.move_paragraphs:
        comments = [line for line in paragraph if not parse_export(line)]
        fresh = []
        for line in paragraph:
            entry = parse_export(line)
            if entry is None:
                continue
            if entry.name in existing:
                skipped_dupes.append(entry.name)
            else:
                fresh.append(f"export {entry.name}={quote(entry.value)}")
                existing.add(entry.name)
        if fresh:
            if vault_lines and vault_lines[-1].strip():
                vault_lines.append("")
            vault_lines.extend(comments)
            vault_lines.extend(fresh)
            appended_any = True
    if appended_any:
        write_atomic(vault, vault_lines)
    return ImportResult(plan=plan, backup_path=backup_path, skipped_dupes=skipped_dupes)


def source_line_for(vault: Path) -> str:
    return f'[ -f "{vault}" ] && source "{vault}"'
