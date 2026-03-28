# Harness

Harness 是执行故事的引擎。它负责阅读故事的叙事内容，理解其中描述的业务操作和预期结果，自动将其转化为实际的测试执行（如 API 调用）。

Harness 本身不包含大模型能力，它通过关联一个 [Provider](providers.md) 来获取大模型支持。

支持的 harness：

| 名称 | 说明 |
|------|------|
| `claude-code` | 使用 Claude Code CLI 作为执行引擎 |
| `claude-agent-sdk` | 使用 Claude Agent SDK 作为执行引擎 |
| `opencode` | 使用 OpenCode 作为执行引擎 |

## GET /api/v1/harnesses

列出所有可用的 harness 及其状态。

**响应**: `200 OK`

```json
{
  "items": [
    {
      "name": "claude-code",
      "available": true,
      "version": "1.0.32",
      "provider": "anthropic-main"
    },
    {
      "name": "claude-agent-sdk",
      "available": true,
      "version": "0.5.1",
      "provider": null
    },
    {
      "name": "opencode",
      "available": false,
      "reason": "binary not found in PATH",
      "provider": null
    }
  ]
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | string | harness 标识 |
| `available` | boolean | 当前环境中是否可用 |
| `version` | string | 检测到的版本号，不可用时为 null |
| `provider` | string\|null | 关联的 provider 名称，null 表示未配置 |
| `reason` | string | 不可用时的原因说明 |

---

## GET /api/v1/harnesses/{harness_name}

获取单个 harness 的详细配置。

**响应**: `200 OK`

```json
{
  "name": "claude-code",
  "available": true,
  "version": "1.0.32",
  "provider": "anthropic-main",
  "config": {
    "timeout_seconds": 300
  }
}
```

### config 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `timeout_seconds` | integer | 单个步骤的超时时间（秒） |

### 错误

| 状态码 | error.code | 场景 |
|--------|------------|------|
| 404 | `resource_not_found` | harness 名称不存在 |

---

## PATCH /api/v1/harnesses/{harness_name}

更新 harness 的配置。只需传入要修改的字段。

**请求**:

```json
{
  "provider": "deepseek-local",
  "config": {
    "timeout_seconds": 600
  }
}
```

**响应**: `200 OK`

返回更新后的完整 harness 对象，格式同 `GET /api/v1/harnesses/{harness_name}`。

### 错误

| 状态码 | error.code | 场景 |
|--------|------------|------|
| 404 | `resource_not_found` | harness 名称不存在 |
| 400 | `validation_error` | 配置字段类型或值不合法 |
| 400 | `validation_error` | 指定的 provider 不存在 |
