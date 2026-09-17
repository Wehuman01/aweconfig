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

它刻意不做的事:切换 agent profile(那是 [aweswitch](https://github.com/wehuman01/aweswitch) 的活)、路由模型流量(那是 [awerouter](https://github.com/wehuman01/awerouter) 的活)、保管 OAuth 登录 token(留在各工具自己的配置里)。它只是这些工具读密钥的保险箱——awerouter 的 `${VAR}` provider 引用直接从本文件喂进去的环境变量解析。

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

## Awesome 软件生态

aweconfig 是一个不断壮大的 "awesome" 工具家族中的一员 — 围绕 AI 编程 agent 打造，local-first、可被 agent 直接操作。

### CLI 工具

- **[aweskill](https://aweskill.wehuman.top/)** — CLI 优先的技能包管理器，支持 48+ AI 编程 agent。
- **[aweswitch](https://github.com/wehuman01/aweswitch)** — Claude Code、Codex、OpenCode 的 agent 配置切换器。
- **[awerouter](https://github.com/wehuman01/awerouter)** — 智能路由器，用结构信号把请求分给 Flash 或 Pro 模型，减少不必要的模型开销。
- **[awecompress](https://github.com/wehuman01/awecompress)** — 面向编程 agent 的透明上下文压缩代理：长会话冻结摘要，可与 awerouter 叠加使用。
- **[aweshelf](https://github.com/wehuman01/aweshelf)** — 收藏、分类、恢复 AI 编程会话，还能搭配 aweswitch 实现保存配置，一键启动。
- **[aweshare](https://github.com/wehuman01/aweshare)** — 通过自建 Hub 共享本地 Ollama/vLLM，或国产厂商 coding plan，或已授权的 OpenAI/Anthropic 帐号订阅，实现 token 的共享经济。
- **[awewarm](https://github.com/wehuman01/awewarm)** — 订阅窗口保持器，让 AI 编程套餐的窗口持续激活，无论是本地设置，还是通过远程连接的服务器。
- **[awewarm-hub](https://github.com/wehuman01/awewarm-hub)** — awewarm 的多租户 Hub 服务器：邀请码、租户容量上限、共享保温窗口。
- **[awescholar](https://github.com/wehuman01/awescholar)** — AI agent 可自主执行的科学文献发现与策展，搜索、标注、筛选和报告学术论文。
- **[awecontrib](https://github.com/wehuman01/awecontrib)** — 每个仓库一条 verify 入口：写入一个小的 verify 脚本和最小 CI，本地和 CI 跑的是同一条命令。

### 桌面应用

- **[awefork](https://github.com/wehuman01/awefork)** — 把 AI 编程 agent 的会话变成一棵树的桌面工作台：任意一轮，随时分叉，每条分支都留着；搭配 aweswitch 用更顺手 — 用 profile 启动会话，再回来分叉它的历史。
- **[awedot](https://awedot.wehuman.top/)** — 悬浮球驻留屏幕边缘，实时追踪当前 AI 会话；一键收藏、随时恢复，并可搭配 aweswitch 固定 agent 配置（比如用 GLM 模型启动）。

### Project Collections

- **[Awesome AI Meets Biology](https://github.com/Webioinfo01/Awesome-AI-Meets-Biology)** — AI 在生物学、生物信息学和生物医学研究中应用的精选综述。由 awescholar 驱动。
- **[Awesome AI Virtual Tumor](https://github.com/Webioinfo01/Awesome-AI-Virtual-Tumor)** — 面向虚拟肿瘤建模与仿真的前沿 AI 系统精选合集：静态模型、动态模型、agent、基准与综述。
- **[AgentX](https://github.com/Webioinfo01/agentx-hub)** — 科研 AI agent 社区目录：Verified Run 评审、实时 GitHub 指标和月度报告，由 awescholar 校验流水线策展。

```bash
uv venv && uv pip install --python .venv/bin/python -e ".[dev]"
./verify   # pytest + ruff,与 CI 一致
```
