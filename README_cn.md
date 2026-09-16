<div align="center">
  <h1>aweconfig: 给 shell 密钥用的笨保险箱</h1>
  <p><strong>一个 0600 的 env 文件,一行 source,zshrc 里不再有密钥。</strong></p>
  <p>
    <a href="./README.md">English</a> ·
    <strong>简体中文</strong>
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

> 一个 0600 的 env 文件,一行 source,zshrc 里不再有密钥。

aweconfig 把所有从环境变量读密钥的工具的 key 集中到一个文件 `~/.config/awe/keys.env`,并提供一个极小的编辑器 CLI。文件本身是普通 shell 文件,任何 POSIX shell 都能直接 `source`——CLI 只是上面的安全编辑器,不是运行时依赖:哪怕 CLI 坏了,shell 照样加载密钥。

它刻意不做的事:切换 agent profile(那是 [aweswitch](https://github.com/Webioinfo01/aweswitch) 的活)、路由模型流量(那是 [awerouter](https://github.com/wehuman01/awerouter) 的活)、保管 OAuth 登录 token(留在各工具自己的配置里)。它只是这些工具读密钥的保险箱——awerouter 的 `${VAR}` provider 引用直接从本文件喂进去的环境变量解析。

## 安装

```bash
pip install aweconfig
```

## 快速开始

```bash
aweconfig init                    # 创建 ~/.config/awe/keys.env(权限 0600)
aweconfig set DEEPSEEK_AUTH_TOKEN # 隐藏输入,不进 shell history
aweconfig list                    # 只列名字,不显示值
aweconfig show DEEPSEEK_AUTH_TOKEN
```

然后在 `~/.zshrc` 加一行(init 会直接打印给你):

```zsh
[ -f "$HOME/.config/awe/keys.env" ] && source "$HOME/.config/awe/keys.env"
```

想把 `~/.zshrc` 里已有的密钥一次性搬出来:

```bash
aweconfig import-zshrc --dry-run  # 先看哪些会搬走、哪些会留下
aweconfig import-zshrc            # 执行迁移,迁移前自动备份 ~/.zshrc
```

## 文件格式

```zsh
# aweconfig vault - plain shell env file; keep mode 0600 and never commit it.

## Anthropic
export GLM_ANTHROPIC_AUTH_TOKEN='...'

## Openai
export OPENAI_AUTH_TOKEN='...'
```

- 路径:`~/.config/awe/keys.env`,可用 `$AWECONFIG_FILE` 覆盖。
- 格式:`export NAME='value'` 行加自由注释。手工编辑完全可以;`aweconfig edit` 用 `$EDITOR` 打开。
- CLI 每次写入都是原子操作(临时文件 + rename),并强制 mode 0600。

## 命令

```bash
aweconfig init                     # 不存在则创建保险箱文件(0600)
aweconfig set NAME [--value V|--stdin]
aweconfig list                     # 密钥名,每行一个
aweconfig show NAME [--raw]
aweconfig rm NAME
aweconfig edit                     # 用 $EDITOR 打开保险箱
aweconfig path                     # 打印保险箱文件路径
aweconfig import-zshrc [--file RC] [--dry-run] [--yes] [--name NAME]
```

`import-zshrc` 只在段落内所有 export 都像密钥(名字含 `TOKEN`、`KEY` 或 `SECRET`)时才整段搬移;混合段落原地不动,`--name` 可强制指定。已存在于保险箱的名字会被跳过,绝不覆盖。

## 开发

```bash
uv venv && uv pip install --python .venv/bin/python -e ".[dev]"
./verify   # pytest + ruff,与 CI 一致
```
