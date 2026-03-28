# test-story harness

Harness 管理命令。Harness 是执行故事的引擎，通过关联 provider 获取大模型能力。

## harness list

列出所有 harness 及其状态。

```bash
test-story harness list
```

输出示例：

```
NAME               AVAILABLE   VERSION   PROVIDER
claude-code        yes         1.0.32    anthropic-main
claude-agent-sdk   yes         0.5.1     -
opencode           no          -         -
```

## harness show

查看单个 harness 的详细配置。

```bash
test-story harness show <name>
```

输出示例：

```
Name:      claude-code
Available: yes
Version:   1.0.32
Provider:  anthropic-main
Timeout:   300s
```

## harness set

更新 harness 配置。

```bash
test-story harness set <name> [options]
```

| 选项 | 说明 |
|------|------|
| `--provider` | 关联大模型供应商 |
| `--timeout` | 单个步骤超时时间（秒） |

```bash
# 切换 claude-code 使用 deepseek 供应商
test-story harness set claude-code --provider deepseek-prod

# 调整超时时间
test-story harness set claude-agent-sdk --timeout 600

# 同时设置
test-story harness set claude-code --provider anthropic-main --timeout 300
```
