# Contributing to aweconfig

## Development setup

```bash
uv venv && uv pip install --python .venv/bin/python -e ".[dev]"
./verify
```

`./verify` runs pytest plus `ruff check .` and is exactly what CI runs. It must be green before every commit.

## Branch model

`dev` is the working branch; `main` receives promoted releases. Releases use `awecontrib bump <version>` for the version carrier and CHANGELOG, then the normal tag-and-release flow.

## Layout

```
src/aweconfig/store.py     # vault file: parse, edit, atomic write, permissions
src/aweconfig/importer.py  # one-way zshrc -> vault migration (plan, rebuild, apply)
src/aweconfig/cli.py       # argparse wiring only, no business logic
tests/                     # one file per source module, real temp dirs, no fs mocking
resources/skills/aweconfig # agent skill that knows when to reach for this CLI
```

## Design constraints

Facts and rules the implementation must keep holding:

- **The vault is the contract, the CLI is not.** The file is a plain shell file of `export NAME='value'` lines and comments. Any POSIX shell must be able to `source` it with no code present. Never move intelligence into the CLI that the file cannot express.
- **Zero runtime dependencies.** stdlib only. Adding a dependency needs a stronger reason than convenience.
- **Every write is atomic** (temp file in the same dir, `chmod 0600`, `os.replace`) so a crash never truncates the vault or relaxes its mode.
- **Values are single-quoted** with the `'\''` idiom on write; the parser accepts single-quoted, double-quoted, and bare forms so hand edits keep working.
- **Migration is paragraph-granular and one-way.** A paragraph (run of non-blank lines) moves only when every export in it matches the secret name pattern (`TOKEN|KEY|SECRET`) or was forced with `--name`. Comments ride along. Names already in the vault are skipped, never overwritten. The rc file always gets a timestamped `.bak-*` backup before it is rewritten.
- **Keys never enter this repo.** Tests use synthetic values only. If a real key ever appears in a diff, the commit does not happen.

## Engineering Taste

Prefer solutions that are simple, clear, decoupled, honest, focused, and durable.

- Simple: make the smallest change that solves the real problem.
- Clear: optimize for the next reader, not for cleverness.
- Decoupled: keep boundaries clean, but do not add abstractions without a real need.
- Honest: make complexity, state, side effects, assumptions, and failure modes visible; do not hide complexity or create extra complexity.
- Focused: preserve boundaries between modules, and keep top-level convenience commands minimal.
- Durable: choose behavior that is easy to maintain, test, and extend.
- First principles: identify the real problem, hard constraints, and known facts before reaching for patterns, abstractions, or prior solutions.
