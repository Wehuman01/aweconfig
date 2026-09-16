<div align="center">
  <h1>aweconfig: The dumb vault for shell keys</h1>
  <p><strong>One 0600 env file. One source line. No more secrets in ~/.zshrc.</strong></p>
  <p>
    <strong>English</strong> ·
    <a href="./README_cn.md">简体中文</a>
  </p>
  <p>
    <img src="https://img.shields.io/badge/version-0.1.0-7C3AED?style=flat-square" alt="Version">
    <img src="https://img.shields.io/badge/python-%E2%89%A5%203.9-0EA5E9?style=flat-square" alt="Python">
  </p>
  <p>
    <img src="https://img.shields.io/badge/status-alpha-c96a3d?style=flat-square" alt="Status">
    <img src="https://img.shields.io/badge/install-pip-22C55E?style=flat-square" alt="pip install">
    <img src="https://img.shields.io/badge/platform-terminal-334155?style=flat-square" alt="Platform">
    <img src="https://img.shields.io/github/stars/wehuman01/aweconfig?style=flat-square" alt="GitHub stars">
  </p>
</div>

> One 0600 env file. One source line. No more secrets in ~/.zshrc.

aweconfig keeps every API key your tools read from the environment in one file, `~/.config/awe/keys.env`, and gives you a tiny editor for it. The file is a plain shell file any POSIX shell can `source` — the CLI is only a safe editor on top, never a runtime dependency. If the CLI disappears, your shell still loads the keys.

What it deliberately does not do: switch agent profiles (that is [aweswitch](https://github.com/Webioinfo01/aweswitch)), route model traffic (that is [awerouter](https://github.com/wehuman01/awerouter)), or hold OAuth login tokens (those stay in each tool's own config). It is just the vault those tools read keys from — awerouter's `${VAR}` provider references resolve straight from the environment this file feeds.

## Install

```bash
pip install aweconfig
```

## Quick Start

```bash
aweconfig init                    # create ~/.config/awe/keys.env (mode 0600)
aweconfig set DEEPSEEK_AUTH_TOKEN # prompts hidden; never touches shell history
aweconfig list                    # names only, no values
aweconfig show DEEPSEEK_AUTH_TOKEN
```

Then add one line to `~/.zshrc` (init prints it for you):

```zsh
[ -f "$HOME/.config/awe/keys.env" ] && source "$HOME/.config/awe/keys.env"
```

To move existing secrets out of `~/.zshrc` in one go:

```bash
aweconfig import-zshrc --dry-run  # shows what would move and what would stay
aweconfig import-zshrc            # moves them, backs up ~/.zshrc first
```

## The file

```zsh
# aweconfig vault - plain shell env file; keep mode 0600 and never commit it.

## Anthropic
export GLM_ANTHROPIC_AUTH_TOKEN='...'

## Openai
export OPENAI_AUTH_TOKEN='...'
```

- Path: `~/.config/awe/keys.env`, overridable with `$AWECONFIG_FILE`.
- Format: `export NAME='value'` lines plus free-form comments. Edit by hand if you like; `aweconfig edit` opens `$EDITOR`.
- Every CLI write is atomic (temp file + rename) and re-asserts mode 0600.

## Commands

```bash
aweconfig init                     # create the vault file (0600) if missing
aweconfig set NAME [--value V|--stdin]
aweconfig list                     # key names, one per line
aweconfig show NAME [--raw]
aweconfig rm NAME
aweconfig edit                     # open the vault in $EDITOR
aweconfig path                     # print the vault file path
aweconfig import-zshrc [--file RC] [--dry-run] [--yes] [--name NAME]
```

`import-zshrc` moves a paragraph only when every export in it looks like a secret (name contains `TOKEN`, `KEY`, or `SECRET`); mixed paragraphs stay put and `--name` forces one through. Names already in the vault are skipped, never overwritten.

## Development

```bash
uv venv && uv pip install --python .venv/bin/python -e ".[dev]"
./verify   # pytest + ruff, same as CI
```
