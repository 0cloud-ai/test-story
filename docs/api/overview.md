# API 概览

## 基础信息

- **基础地址**: `http://localhost:3000`
- **API 前缀**: `/api/v1`
- **协议**: HTTP/1.1
- **数据格式**: JSON（`Content-Type: application/json`），故事上传除外（`text/markdown`）

## 版本策略

API 通过 URL 路径进行版本管理（`/api/v1/...`）。当前版本为 `v1`。

## 认证

v1 为本地运行模式，不需要认证。

## 分页

列表类端点统一使用以下分页参数：

**请求参数（Query）**:

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `page` | integer | 1 | 页码，从 1 开始 |
| `per_page` | integer | 20 | 每页条数，最大 100 |

**响应格式**:

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "per_page": 20
}
```

## 错误格式

所有错误响应使用统一格式：

```json
{
  "error": {
    "code": "resource_not_found",
    "message": "Story with id 'story_abc123' does not exist"
  }
}
```

### 通用错误码

| HTTP 状态码 | error.code | 说明 |
|------------|------------|------|
| 400 | `bad_request` | 请求格式错误 |
| 400 | `validation_error` | 字段校验失败 |
| 404 | `resource_not_found` | 资源不存在 |
| 409 | `conflict` | 资源冲突（如重复创建） |
| 422 | `unprocessable` | 请求可解析但语义有误（如故事缺少 meta 块） |
| 500 | `internal_error` | 服务器内部错误 |

## 资源模型

```
Collection  (故事集，对应一个软件迭代周期)
  └── Story  (markdown 故事文件)
        └── Run  (一次故事执行)
              └── Step  (harness 从故事中提取的单个测试步骤)

Harness   (执行引擎：claude-code / claude-agent-sdk / opencode)
  └── 关联一个 Provider

Provider  (大模型供应商：anthropic / openai / deepseek / ollama / custom)
```

## 端点总览

| 文档 | 资源 | 端点数 |
|------|------|--------|
| [server.md](server.md) | 服务器 | 3 |
| [providers.md](providers.md) | 大模型供应商 | 5 |
| [harnesses.md](harnesses.md) | Harness | 3 |
| [collections.md](collections.md) | 故事集 | 6 |
| [stories.md](stories.md) | 故事 | 5 |
| [runs.md](runs.md) | 运行 | 7 |
| [steps.md](steps.md) | 步骤 | 2 |

**共计 31 个端点**。
