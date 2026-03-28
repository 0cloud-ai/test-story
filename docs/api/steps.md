# 步骤（Steps）

步骤是 harness 在执行故事时自动提取的测试单元。每个步骤对应故事中的一段业务逻辑描述。步骤是只读的，由 harness 在运行过程中生成。

步骤使用 `index`（从 1 开始）而非 ID 来标识，因为步骤是有序的，与故事章节结构对应。

## GET /api/v1/runs/{run_id}/steps

列出某次运行的所有步骤。

**查询参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| `status` | string | 按状态过滤：`passed`、`failed`、`running`、`pending`、`error` |

**响应**: `200 OK`

```json
{
  "items": [
    {
      "index": 1,
      "chapter": "第一章 初来乍到",
      "description": "注册用户叶知秋",
      "status": "passed",
      "duration_ms": 340
    },
    {
      "index": 2,
      "chapter": "第一章 初来乍到",
      "description": "重复注册同一用户名和邮箱，预期被拒绝",
      "status": "passed",
      "duration_ms": 210
    },
    {
      "index": 3,
      "chapter": "第一章 初来乍到",
      "description": "不填邮箱注册，预期字段校验失败",
      "status": "passed",
      "duration_ms": 185
    },
    {
      "index": 4,
      "chapter": "第二章 寻找一本书",
      "description": "搜索关键词'三体'",
      "status": "passed",
      "duration_ms": 520
    },
    {
      "index": 5,
      "chapter": "第二章 寻找一本书",
      "description": "搜索不存在的关键词，预期空结果",
      "status": "passed",
      "duration_ms": 190
    },
    {
      "index": 6,
      "chapter": "第二章 寻找一本书",
      "description": "超大页码搜索，预期空结果且不报错",
      "status": "passed",
      "duration_ms": 200
    }
  ],
  "total": 12
}
```

### 错误

| 状态码 | error.code | 场景 |
|--------|------------|------|
| 404 | `resource_not_found` | 运行不存在 |

---

## GET /api/v1/runs/{run_id}/steps/{step_index}

获取单个步骤的完整详情，包含 harness 实际执行的请求和断言结果。

**响应**: `200 OK`

```json
{
  "index": 2,
  "chapter": "第一章 初来乍到",
  "description": "重复注册同一用户名和邮箱，预期被拒绝",
  "status": "passed",
  "narrative": "陆青用同样的用户名和邮箱又注册了一次，系统识别出这是重复注册，拒绝了，并且告诉他这个用户名或邮箱已经存在。",
  "actual": {
    "method": "POST",
    "url": "/api/v1/users/register",
    "request_body": {
      "username": "叶知秋",
      "email": "yezhiqiu@mail.com",
      "password": "Qiuye#1998"
    },
    "status_code": 409,
    "response_body": {
      "error": {
        "code": "user_already_exists",
        "message": "该用户名或邮箱已被注册"
      }
    }
  },
  "assertions": [
    {
      "description": "系统识别出重复注册",
      "expected": "请求被拒绝",
      "actual": "409 Conflict",
      "passed": true
    },
    {
      "description": "提示用户名或邮箱已存在",
      "expected": "错误信息包含'已存在'相关描述",
      "actual": "该用户名或邮箱已被注册",
      "passed": true
    }
  ],
  "duration_ms": 210,
  "started_at": "2026-03-28T10:05:03Z",
  "finished_at": "2026-03-28T10:05:03Z"
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `narrative` | string | 故事中对应这个步骤的原文片段 |
| `actual` | object | harness 实际发出的请求和收到的响应 |
| `assertions` | array | harness 根据故事叙述提取的断言列表 |
| `assertions[].expected` | string | harness 从故事中理解到的预期行为 |
| `assertions[].actual` | string | 实际执行结果的摘要 |

### 错误

| 状态码 | error.code | 场景 |
|--------|------------|------|
| 404 | `resource_not_found` | 运行或步骤不存在 |
