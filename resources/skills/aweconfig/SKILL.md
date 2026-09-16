---
name: aweconfig
description: "Use when managing shared API keys for shell tools: creating the 0600 keys.env vault, adding or rotating a key without shell history, listing masked keys, or migrating secret exports out of ~/.zshrc. Covers pointing tools (awerouter ${VAR} refs) at vault-fed env vars. 中文触发词：密钥管理、换key、加key、轮换密钥、zshrc迁移、keys.env、保险箱、aweconfig。"
---

# aweconfig

One 0600 env file (`~/.config/awe/keys.env`), one source line in the shell rc. The CLI is only a safe editor on top of a plain shell file — never a runtime dependency.

## When to reach for it

- "帮我把这个 key 换掉 / 加一个 key" → `aweconfig set NAME` (hidden prompt; `--stdin` for pipes)
- "看看现在有哪些密钥" → `aweconfig list` (names only), `aweconfig show NAME` (masked)
- "把 zshrc 里的密钥搬出去" → `aweconfig import-zshrc --dry-run` first, review, then run without `--dry-run`
- "某个工具要读密钥" → tools read env vars; the rc sources the vault. `aweconfig path` prints it.

## Rules

- Real keys live only in the vault file, never in any repo, script, or chat output. `show --raw` is for piping into a tool, not for displaying.
- Migration moves a paragraph only when every export in it looks like a secret (`TOKEN|KEY|SECRET` in the name); mixed paragraphs stay put. `--name NAME` forces one through. A timestamped `.bak-*` of the rc file is always written first.
- aweconfig does not switch profiles (aweswitch), route traffic (awerouter), or store OAuth tokens. Do not grow it toward those.
- `$AWECONFIG_FILE` overrides the vault path — use it for tests and demos, never point it at a file inside a git repo.
