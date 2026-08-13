# Git Agent for Pi ![](https://img.shields.io/badge/runtime-Pi-blue)

[![Version](https://img.shields.io/npm/v/pi-git-agent)](https://www.npmjs.com/package/pi-git-agent) [![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[English](README.md) | **简体中文**

一个 Pi 编码代理包,把 `git-agent` 变成原生的 `/git-agent` 命令菜单:原子 AI 提交、共同变更分析,以及把裸 `git add`/`git commit` 重定向到原子提交流程的防护。无 skill 面。

## 概览

- **原子提交**:把暂存的改动拆成最多 5 个逻辑独立的提交,用 AI 生成 Conventional Commit 消息(`git-agent commit`)。
- **共同变更分析**:从 git 历史中挖掘一起变化的文件和测试套件(`git-agent related`)。
- **原生扩展防护**:`extensions/validate-commit.ts` 拦截裸 `git commit` / `git add` 工具调用,引导代理改用 `git-agent` 原子提交。
- **会话驱动的提交**:`extensions/session-context.ts` 提供 `session_context` 工具,读取当前会话记录,让提交意图来自用户实际提出的请求,而不是一句压缩的话。
- **自动模型身份识别**:`git-agent` 自动检测代理环境变量(`PI_MODEL`、`CLAUDE_CODE_MODEL`、`CODEX_MODEL`、`MODEL`),无需手动传递 co-author 标志。

## 用法

输入 `/git-agent` 打开原生菜单:

```
git-agent workflows:
❯ 1. Commit changes        (procedures/commit.md)
  2. Commit and push       (procedures/commit-and-push.md)
  3. Init / optimize       (procedures/init.md)
  4. Related files & tests (procedures/related.md)
```

或者直接传一个工作流关键字跳过菜单:

```bash
/git-agent commit                # 用会话上下文构建 intent 提交
/git-agent commit --co-author "Alice <a@example.com>"
/git-agent related src/foo.ts    # 查询指定文件的共同变更
/git-agent related --tests src/
/git-agent init                  # 重新生成 scopes + .gitignore
```

每次选择都会通过 `pi.sendUserMessage` 把完整流程(`procedures/*.md`)嵌入下一条消息,并注入一小段引导,让自然语言请求("commit this"、"commit and push")直接路由到对应流程。

## 安装

```bash
# 已发布版本
pi install npm:pi-git-agent
# 或本地安装:pi install /path/to/git-agent/pi-git-agent
```

需要 PATH 上有 `git-agent` CLI(由本仓库的 `git-agent-cli/` 目录构建)。

## 文件

```
pi-git-agent/
├── extensions/
│   ├── menu.ts               # /git-agent 命令菜单 + 引导注入
│   ├── session-context.ts    # session_context 工具(提交意图来源)
│   └── validate-commit.ts    # 拦截裸 git add/commit,重定向到 git-agent
├── procedures/
│   ├── commit.md             # 原子 AI 提交流程
│   ├── commit-and-push.md    # 提交 + 推送流程
│   ├── init.md               # scope/.gitignore 重新生成
│   └── related.md            # 共同变更查询
└── references/
    ├── cli.md                # git-agent CLI 参考
    └── coauthor-attribution.md
```

## License

[MIT](LICENSE)
