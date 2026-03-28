# test-story server

服务器管理命令。

## server start

启动本地服务器。

```bash
test-story server start [options]
```

| 选项 | 缩写 | 说明 | 默认值 |
|------|------|------|--------|
| `--port` | `-p` | 监听端口 | `3000` |
| `--harness` | | 默认 harness | `claude-code` |
| `--provider` | | 默认大模型供应商 | |
| `--daemon` | `-d` | 后台运行 | `false` |

```bash
# 默认启动
test-story server start

# 指定端口，后台运行
test-story server start -p 8000 -d

# 指定默认 harness 和 provider
test-story server start --harness claude-agent-sdk --provider anthropic-main
```

## server stop

停止后台运行的服务器。

```bash
test-story server stop
```

## server status

查看服务器状态。

```bash
test-story server status
```

输出示例：

```
Server:  http://localhost:3000
Status:  running
Version: 0.1.0
Uptime:  1h 23m 45s
Harness: claude-code
Provider: anthropic-main
Scenes:  api
```

## server config

查看或更新服务器配置。

```bash
# 查看配置
test-story server config

# 更新配置
test-story server config --harness claude-agent-sdk --provider deepseek-local
test-story server config --max-concurrent-runs 5
```

| 选项 | 说明 |
|------|------|
| `--harness` | 设置默认 harness |
| `--provider` | 设置默认大模型供应商 |
| `--max-concurrent-runs` | 设置最大并发运行数 |
