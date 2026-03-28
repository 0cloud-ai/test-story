# 大模型供应商（Providers）

Provider 是大模型供应商的配置。每个 provider 代表一个可调用的大模型服务端点，包含供应商类型、API 地址、认证信息和模型参数。Harness 执行故事时，通过关联的 provider 来调用大模型能力。

同一个供应商类型可以录入多个 provider（例如两个不同的 Anthropic 账号，或一个指向官方 API、一个指向代理）。

## POST /api/v1/providers

录入一个大模型供应商。

**请求**:

```json
{
  "name": "anthropic-main",
  "type": "anthropic",
  "config": {
    "base_url": "https://api.anthropic.com",
    "api_key": "sk-ant-xxxxx",
    "model": "claude-sonnet-4-6",
    "max_tokens": 16384
  }
}
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 供应商名称，需唯一，用于 harness 引用 |
| `type` | string | 是 | 供应商类型：`anthropic`、`openai`、`deepseek`、`ollama`、`custom` |
| `config` | object | 是 | 供应商���置 |

### config 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `base_url` | string | 是 | API 基础地址 |
| `api_key` | string | 否 | API 密钥（ollama 等本地模型不需要） |
| `model` | string | 是 | 默认模型标识 |
| `max_tokens` | integer | 否 | 单次调用最大 token 数，默认 16384 |

**响应**: `201 Created`

```json
{
  "id": "prov_d4e5f6",
  "name": "anthropic-main",
  "type": "anthropic",
  "config": {
    "base_url": "https://api.anthropic.com",
    "api_key": "sk-ant-***",
    "model": "claude-sonnet-4-6",
    "max_tokens": 16384
  },
  "created_at": "2026-03-28T10:00:00Z",
  "updated_at": "2026-03-28T10:00:00Z"
}
```

> 注意：响应中的 `api_key` 会被脱敏显示。

### 错误

| 状态码 | error.code | 场景 |
|--------|------------|------|
| 400 | `validation_error` | 必填字段缺失或 type 不支持 |
| 409 | `conflict` | 同名 provider 已存在 |

---

## GET /api/v1/providers

列出所有已录入的大模型供应商。

**查询参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| `type` | string | 按供应商类型过滤 |
| `page` | integer | 页码 |
| `per_page` | integer | 每页条数 |

**响应**: `200 OK`

```json
{
  "items": [
    {
      "id": "prov_d4e5f6",
      "name": "anthropic-main",
      "type": "anthropic",
      "config": {
        "base_url": "https://api.anthropic.com",
        "api_key": "sk-ant-***",
        "model": "claude-sonnet-4-6",
        "max_tokens": 16384
      },
      "created_at": "2026-03-28T10:00:00Z",
      "updated_at": "2026-03-28T10:00:00Z"
    },
    {
      "id": "prov_g7h8i9",
      "name": "deepseek-local",
      "type": "deepseek",
      "config": {
        "base_url": "https://api.deepseek.com",
        "api_key": "sk-ds-***",
        "model": "deepseek-chat",
        "max_tokens": 8192
      },
      "created_at": "2026-03-28T10:01:00Z",
      "updated_at": "2026-03-28T10:01:00Z"
    }
  ],
  "total": 2,
  "page": 1,
  "per_page": 20
}
```

---

## GET /api/v1/providers/{provider_id}

获取单个供应商的详细信息。

**响应**: `200 OK`

格式同列表中的单个对象。

### 错误

| 状态码 | error.code | 场景 |
|--------|------------|------|
| 404 | `resource_not_found` | 供应商不存在 |

---

## PATCH /api/v1/providers/{provider_id}

更新供应商配置。只需传入要修改的字段。

**请求**:

```json
{
  "config": {
    "model": "claude-opus-4-6",
    "max_tokens": 32768
  }
}
```

**响应**: `200 OK`

返回更新后的完整供应商对象。

### 错误

| 状态码 | error.code | 场景 |
|--------|------------|------|
| 404 | `resource_not_found` | 供应商不存在 |
| 400 | `validation_error` | 配置字段类型或值不合法 |

---

## DELETE /api/v1/providers/{provider_id}

删除一个供应商。

**响应**: `204 No Content`

### 错误

| 状态码 | error.code | 场景 |
|--------|------------|------|
| 404 | `resource_not_found` | 供应商不存在 |
| 409 | `conflict` | 该供应商正在被某个 harness 使用 |
