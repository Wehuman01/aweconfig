# aweconfig Bootstrap Protocol

This document is for AI coding agents. Help the user install and configure `aweconfig`, a 0600 shell-env vault that keeps every API key in one `keys.env` file which the user's zshrc sources with a single line. There is a tiny editor CLI on top; if the CLI disappeared tomorrow, the shell setup would keep working.

## Everything Is Local

aweconfig has zero runtime dependencies and performs no network requests. All secrets live in one file (`~/.config/awe/keys.env`, mode 0600). Never print, copy, or paste secret values into chat: `aweconfig show <name>` masks values by default, and that is the only display form you should ever relay.

## Language Behavior

- Reply in the user's language when possible.
- If the user asks in Chinese, continue in Chinese.
- If the user asks in English, continue in English.

## Step 1: Install the CLI

### Prerequisites

- Python >= 3.9 (`python3 --version`)
- pip available (`pip3 --version`)

### Steps

```bash
pip3 install aweconfig
aweconfig -v
```

Expected output: `aweconfig 0.1.0` (or newer).

---

## Step 2: Install the aweconfig skill

Install the skill so the agent can manage the vault in this and future sessions. Choose one of the following options.

### Option A: Via aweskill (recommended if aweskill is available)

```bash
aweskill install wehuman01/aweconfig
aweskill agent add skill aweconfig --global --agent <agent-id>
```

`<agent-id>`: run `aweskill agent supported` and look for the `✓` line matching the current agent. If you cannot determine it, ask the user.

### Option B: Direct copy (no aweskill needed)

Determine the current agent's global skill directory (Claude Code: `~/.claude/skills/aweconfig/`, Codex: `~/.codex/skills/aweconfig/`, Cursor: `.cursor/skills/aweconfig/`, Gemini CLI: `~/.gemini/skills/aweconfig/`, OpenCode: `~/.opencode/skills/aweconfig/`). If the agent is not in this list, ask the user where to place the skill file.

```bash
mkdir -p <skill-directory>
curl -fsSL https://raw.githubusercontent.com/wehuman01/aweconfig/main/resources/skills/aweconfig/SKILL.md -o <skill-directory>/SKILL.md
```

---

## Step 3: First-run setup (interactive — the user runs it)

`aweconfig set` prompts with input hidden, `aweconfig edit` opens `$EDITOR`, and `aweconfig import-zshrc` asks for confirmation — all three belong in the user's terminal. Tell the user:

> Run `aweconfig init` once, then move your existing key exports over: `aweconfig import-zshrc --dry-run` first to preview the plan, then `aweconfig import-zshrc` to apply it. It makes a timestamped backup of your rc file and rewrites the exports into one sourced `keys.env`.

`import-zshrc` is one-way (rc file → vault). Re-running it is safe; already-moved exports are skipped.

## Useful commands

Read-only (safe to run in agent):

```bash
aweconfig list          # key names only, never values
aweconfig show <name>   # masked value
aweconfig path          # vault file location
```

User-run (interactive or touches secrets):

```bash
aweconfig init                      # create the vault (0600) if missing
aweconfig set <name>                # prompts hidden; --value/--stdin exist but expose values
aweconfig edit                      # open the vault in $EDITOR
aweconfig rm <name>                 # remove one key (confirm first)
aweconfig import-zshrc [--dry-run]  # one-way migration from a shell rc
```

## Safety Rules

- Never relay an unmasked value (`show <name> --raw`) into chat or a log.
- Never hand-edit `keys.env` in the agent; go through the CLI or the user's editor.
- `set --value` puts the secret into shell history — prefer the prompted form and say so.
- If a command fails, report the exact command and error message. Do not silently retry.

## Final Step

After setup, tell the user to invoke skills (`/` in Claude Code, `$` in Codex, or the equivalent in other agents) and check that `aweconfig` appears. If not, restart the agent.

> aweconfig is installed and configured. Your keys now live in one 0600 file sourced by your zshrc. From here you can ask me things like:
>
> - "Which key names are in my vault?"
> - "Add a placeholder entry for OPENROUTER_API_KEY — I'll fill in the value myself."
> - "Dry-run the zshrc import before I commit to it."
