# 服务器管理

## GET /healthz

健康检查。

**响应**: `200 OK`

```json
{
  "status": "ok",
  "version": "0.1.0",
  "uptime_seconds": 3600
}
```

---

## GET /api/v1/config

获取当前服务器配置。

**响应**: `200 OK`

```json
{
  "harness": "claude-code",
  "provider": "anthropic-main",
  "supported_scenes": ["api"],
  "max_concurrent_runs": 3
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `harness` | string | 当前默认 harness，可选值：`claude-code`、`claude-agent-sdk`、`opencode` |
| `provider` | string | 当前默认大模型供应商名称 |
| `supported_scenes` | string[] | 当前支持的场景类型 |
| `max_concurrent_runs` | integer | 最大并发运行数 |

---

## PATCH /api/v1/config

更新服务器配置。只需传入要修改的字段。

**请求**:

```json
{
  "harness": "claude-agent-sdk",
  "provider": "deepseek-local",
  "max_concurrent_runs": 5
}
```

**响应**: `200 OK`

返回更新后的完整配置对象，格式同 `GET /api/v1/config`。

### 错误

| 状态码 | error.code | 场景 |
|--------|------------|------|
| 400 | `validation_error` | harness 名称不合法或 max_concurrent_runs 不是正整数 |
