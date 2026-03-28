# CLI 概览

## 安���

```bash
npm install -g test-story
```

## 基本用法

```bash
test-story <command> [subcommand] [options]
```

## 全局选项

| 选项 | 缩写 | 说明 | 默认值 |
|------|------|------|--------|
| `--server` | `-s` | 服务器地址 | `http://localhost:3000` |
| `--output` | `-o` | 输出格式：`text`、`json` | `text` |
| `--help` | `-h` | 显示帮助信息 | |
| `--version` | `-v` | 显示版本号 | |

## 命令一览

| 命令 | 说明 | 文档 |
|------|------|------|
| `test-story server` | 服务器管理 | [server.md](server.md) |
| `test-story provider` | 大模型供应商���理 | [provider.md](provider.md) |
| `test-story harness` | Harness 管理 | [harness.md](harness.md) |
| `test-story collection` | 故事集管理 | [collection.md](collection.md) |
| `test-story story` | 故事管理 | [story.md](story.md) |
| `test-story run` | 执行与查看运行 | [run.md](run.md) |

## 快速开始

```bash
# 1. 启动服务器
test-story server start

# 2. 录入大模型供应商
test-story provider add anthropic-main \
  --type anthropic \
  --base-url https://api.anthropic.com \
  --api-key sk-ant-xxxxx \
  --model claude-sonnet-4-6

# 3. 为 harness 配置供应商
test-story harness set claude-code --provider anthropic-main

# 4. 创建故事集
test-story collection create v2.1-sprint3

# 5. 添加故事
test-story story add v2.1-sprint3 stories/story1.md

# 6. 执行单个故事并实时查看进度
test-story run stories/story1.md

# 7. 执行整个故事集
test-story run --collection v2.1-sprint3
```
