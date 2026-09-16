"""Command-line interface: thin wiring over store and importer."""

from __future__ import annotations

import argparse
import getpass
import os
import subprocess
import sys
from pathlib import Path

from . import __version__, importer, store


def _fail(message: str) -> int:
    print(f"error: {message}", file=sys.stderr)
    return 1


def cmd_init(_args: argparse.Namespace) -> int:
    path = store.keys_path()
    state = store.init_file(path)
    verb = "already exists" if state == "exists" else "created"
    print(f"{path} {verb} (mode 0600)")
    print(f'add this one line to your shell rc: {importer.source_line_for(path)}')
    return 0


def cmd_set(args: argparse.Namespace) -> int:
    if not store.valid_name(args.name):
        return _fail(f"{args.name!r} is not a valid environment variable name.")
    if args.value is not None:
        value = args.value
    elif args.stdin:
        value = sys.stdin.readline().rstrip("\n")
    else:
        value = getpass.getpass(f"value for {args.name} (input hidden): ")
    if not value:
        return _fail("empty value; nothing written.")
    path = store.keys_path()
    replaced = store.set_entry(path, args.name, value)
    print(f"{path}: {'updated' if replaced else 'added'} {args.name}")
    return 0


def cmd_list(_args: argparse.Namespace) -> int:
    for entry in store.read_entries(store.keys_path()):
        print(entry.name)
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    path = store.keys_path()
    for entry in store.read_entries(path):
        if entry.name == args.name:
            print(entry.value if args.raw else store.mask(entry.value))
            return 0
    return _fail(f"{args.name} not in {path}. Run 'aweconfig list' to see names.")


def cmd_rm(args: argparse.Namespace) -> int:
    path = store.keys_path()
    if store.remove_entry(path, args.name):
        print(f"{path}: removed {args.name}")
        return 0
    return _fail(f"{args.name} not in {path}. Run 'aweconfig list' to see names.")


def cmd_path(_args: argparse.Namespace) -> int:
    print(store.keys_path())
    return 0


def cmd_edit(_args: argparse.Namespace) -> int:
    path = store.keys_path()
    if not path.exists():
        return _fail(f"{path} does not exist. Run 'aweconfig init' first.")
    editor = os.environ.get("EDITOR", "vi")
    return subprocess.call([editor, str(path)])


def cmd_import(args: argparse.Namespace) -> int:
    rc_path = Path(args.file).expanduser()
    if not rc_path.exists():
        return _fail(f"{rc_path} not found. Pass --file /path/to/rc.")
    vault = store.keys_path()
    plan = importer.plan_import(
        rc_path.read_text(encoding="utf-8"),
        extra_names=tuple(args.name),
        source_line=importer.source_line_for(vault),
    )
    if plan is None:
        print(f"nothing to move: no secret-looking exports found in {rc_path}")
        return 0

    print(f"would move {len(plan.moved)} export(s) from {rc_path} to {vault}:")
    for name in plan.moved_names:
        print(f"  move  {name}")
    for name in plan.kept:
        print(f"  keep  {name}")
    if plan.kept:
        print("(kept names lack TOKEN/KEY/SECRET; pass --name NAME to force one through)")

    if args.dry_run:
        return 0
    if not args.yes:
        answer = input("Proceed? [y/N] ")
        if answer.strip().lower() not in ("y", "yes"):
            print("aborted; nothing changed")
            return 0

    store.init_file(vault)
    result = importer.apply_import(plan, rc_path, vault)
    print(f"moved {len(plan.moved_names)} export(s); backup at {result.backup_path}")
    if result.skipped_dupes:
        print(f"skipped (already in vault): {', '.join(result.skipped_dupes)}")
    print(f"run 'source {vault}' or open a new shell to pick up the keys")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aweconfig",
        description="Manage the shared keys.env vault for shell tools.",
    )
    parser.add_argument("-v", "--version", action="version", version=f"aweconfig {__version__}")
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    p_init = sub.add_parser("init", help="Create the vault file (0600) if missing.")
    p_init.set_defaults(func=cmd_init)

    p_set = sub.add_parser("set", help="Add or update one key (prompts hidden).")
    p_set.add_argument("name")
    p_set.add_argument("--value", help="Value on the command line (visible in history).")
    p_set.add_argument("--stdin", action="store_true", help="Read the value from stdin.")
    p_set.set_defaults(func=cmd_set)

    p_list = sub.add_parser("list", help="List key names, one per line.")
    p_list.set_defaults(func=cmd_list)

    p_show = sub.add_parser("show", help="Show one key, masked by default.")
    p_show.add_argument("name")
    p_show.add_argument("--raw", action="store_true", help="Print the full value.")
    p_show.set_defaults(func=cmd_show)

    p_rm = sub.add_parser("rm", help="Remove one key.")
    p_rm.add_argument("name")
    p_rm.set_defaults(func=cmd_rm)

    p_edit = sub.add_parser("edit", help="Open the vault in $EDITOR.")
    p_edit.set_defaults(func=cmd_edit)

    p_path = sub.add_parser("path", help="Print the vault file path.")
    p_path.set_defaults(func=cmd_path)

    p_import = sub.add_parser("import-zshrc", help="Move secret exports from a shell rc into the vault.")
    p_import.add_argument("--file", default="~/.zshrc", help="Shell rc to read (default ~/.zshrc).")
    p_import.add_argument("--name", action="append", default=[], help="Force this name to move (repeatable).")
    p_import.add_argument("--dry-run", action="store_true", help="Show the plan, change nothing.")
    p_import.add_argument("--yes", action="store_true", help="Skip the confirmation prompt.")
    p_import.set_defaults(func=cmd_import)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 2
    return args.func(args)
