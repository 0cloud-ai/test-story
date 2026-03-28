# test-story provider

大模型供应商管理命令。

## provider add

录入一个大模型供应商。

```bash
test-story provider add <name> [options]
```

| 选项 | 必填 | 说明 |
|------|------|------|
| `--type` | 是 | 供应商类型：`anthropic`、`openai`、`deepseek`、`ollama`、`custom` |
| `--base-url` | 是 | API 基础地址 |
| `--api-key` | 否 | API 密钥 |
| `--model` | 是 | 默认模型标识 |
| `--max-tokens` | 否 | 单次调用最大 token 数，默认 16384 |

```bash
# Anthropic
test-story provider add anthropic-main \
  --type anthropic \
  --base-url https://api.anthropic.com \
  --api-key sk-ant-xxxxx \
  --model claude-sonnet-4-6

# DeepSeek
test-story provider add deepseek-prod \
  --type deepseek \
  --base-url https://api.deepseek.com \
  --api-key sk-ds-xxxxx \
  --model deepseek-chat

# 本地 Ollama（不需要 api-key）
test-story provider add ollama-local \
  --type ollama \
  --base-url http://localhost:11434 \
  --model llama3
```

## provider list

列出所有已录入的供应商。

```bash
test-story provider list [options]
```

| 选项 | 说明 |
|------|------|
| `--type` | 按类型过滤 |

输出示例：

```
NAME             TYPE        MODEL              BASE URL
anthropic-main   anthropic   claude-sonnet-4-6   https://api.anthropic.com
deepseek-prod    deepseek    deepseek-chat       https://api.deepseek.com
ollama-local     ollama      llama3              http://localhost:11434
```

## provider show

查看单个供应商的详细信息。

```bash
test-story provider show <name-or-id>
```

输出示例：

```
Name:       anthropic-main
ID:         prov_d4e5f6
Type:       anthropic
Base URL:   https://api.anthropic.com
API Key:    sk-ant-***
Model:      claude-sonnet-4-6
Max Tokens: 16384
Created:    2026-03-28 10:00:00
```

## provider update

更新供应商配置。

```bash
test-story provider update <name-or-id> [options]
```

| 选项 | 说明 |
|------|------|
| `--model` | 更新模型标识 |
| `--base-url` | 更新 API 地址 |
| `--api-key` | 更新 API 密钥 |
| `--max-tokens` | 更新最大 token 数 |

```bash
test-story provider update anthropic-main --model claude-opus-4-6 --max-tokens 32768
```

## provider remove

删除一个供应商。正在被 harness 引用的供应商无法删除。

```bash
test-story provider remove <name-or-id>
```

```bash
test-story provider remove ollama-local
# Provider 'ollama-local' removed.

test-story provider remove anthropic-main
# Error: Provider 'anthropic-main' is in use by harness 'claude-code'.
```
