# 运行（Runs）

Run 是一次故事的执行。故事提交给 harness 后，harness 阅读故事内容，理解其中的业务操作和预期结果，自动将其转化为实际的测试执行。

## 状态机

```
queued → running → passed | failed | error | cancelled
```

- **queued**: 已提交，排队等待执行
- **running**: harness 正在执行
- **passed**: 所有步骤通过
- **failed**: 至少一个步骤的断言失败
- **error**: harness 崩溃或超时
- **cancelled**: 被用户取消

## 配置优先级

运行时的 `target` 和 `harness` 按以下优先级确定：

```
run 请求参数 > 故事 meta 块 > 故事集默认配置 > 服务器默认配置
```

---

## POST /api/v1/runs

快捷运行：上传故事并立即执行。对应 CLI 的 `test-story run stories/story1.md`。

**请求**: `Content-Type: multipart/form-data`

| 字段 | 类型 | 必填 | 说��� |
|------|------|------|------|
| `story` | file | 是 | markdown 故事文件 |
| `options` | JSON string | 否 | 运行时覆盖参数 |

`options` 格式：

```json
{
  "target": "http://localhost:8080",
  "harness": "claude-code",
  "collection_id": "coll_a1b2c3",
  "env": {
    "AUTH_TOKEN": "test-token-xxx"
  }
}
```

如果指定了 `collection_id`，故事会被加入该故事集；否则故事不归属于任何故事集。

**响应**: `202 Accepted`

```json
{
  "story": {
    "id": "story_x1y2z3",
    "title": "叶知秋的书店奇遇"
  },
  "run": {
    "id": "run_p1q2r3",
    "status": "queued",
    "created_at": "2026-03-28T10:05:00Z"
  }
}
```

---

## POST /api/v1/stories/{story_id}/runs

执行一个已存在的故事。

**请求（可选覆盖）**:

```json
{
  "target": "http://staging:8080",
  "harness": "claude-agent-sdk",
  "env": {
    "AUTH_TOKEN": "test-token-xxx"
  }
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `target` | string | 否 | 覆盖测试目标地址 |
| `harness` | string | 否 | 覆盖 harness |
| `env` | object | 否 | 运行时环境变量，传递给 harness |

**响应**: `202 Accepted`

```json
{
  "id": "run_p1q2r3",
  "story_id": "story_x1y2z3",
  "status": "queued",
  "harness": "claude-agent-sdk",
  "target": "http://staging:8080",
  "created_at": "2026-03-28T10:05:00Z"
}
```

### ���误

| 状态码 | error.code | 场景 |
|--------|------------|------|
| 404 | `resource_not_found` | 故事不存在 |

---

## GET /api/v1/runs

列出所有运行。

**查询参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| `story_id` | string | 按故事过滤 |
| `collection_id` | string | 按故事集过滤 |
| `batch_id` | string | 按批次过滤（故事集整体执行产生的批次） |
| `status` | string | 按状态过滤：`queued`、`running`、`passed`、`failed`、`error`、`cancelled` |
| `page` | integer | 页码 |
| `per_page` | integer | 每页条数 |

**响���**: `200 OK`

```json
{
  "items": [
    {
      "id": "run_p1q2r3",
      "story_id": "story_x1y2z3",
      "story_title": "叶知秋的书店奇遇",
      "batch_id": null,
      "status": "running",
      "harness": "claude-code",
      "target": "http://localhost:8080",
      "step_summary": {
        "total": 12,
        "passed": 5,
        "failed": 0,
        "running": 1,
        "pending": 6
      },
      "created_at": "2026-03-28T10:05:00Z",
      "started_at": "2026-03-28T10:05:02Z",
      "finished_at": null
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 20
}
```

---

## GET /api/v1/runs/{run_id}

获取单个运行的完整详情，包含所有步骤。

**响应**: `200 OK`

```json
{
  "id": "run_p1q2r3",
  "story_id": "story_x1y2z3",
  "story_title": "叶知秋的书店奇遇",
  "batch_id": null,
  "status": "passed",
  "harness": "claude-code",
  "target": "http://localhost:8080",
  "step_summary": {
    "total": 12,
    "passed": 12,
    "failed": 0
  },
  "steps": [
    {
      "index": 1,
      "chapter": "第一章 初来乍到",
      "description": "注册用户叶知秋",
      "status": "passed",
      "actual": {
        "method": "POST",
        "url": "/api/v1/users/register",
        "status_code": 201,
        "body_summary": "创建用户成功，返回 user_id 和角色"
      },
      "assertions": [
        { "description": "身份标记为普通读者", "passed": true },
        { "description": "密码未被回显", "passed": true }
      ],
      "duration_ms": 340,
      "started_at": "2026-03-28T10:05:02Z",
      "finished_at": "2026-03-28T10:05:03Z"
    }
  ],
  "created_at": "2026-03-28T10:05:00Z",
  "started_at": "2026-03-28T10:05:02Z",
  "finished_at": "2026-03-28T10:05:17Z",
  "duration_ms": 15230
}
```

### 字段说明

**step.actual**: harness 实际执行的 API 调用记录。这是 harness 阅读故事后自行决定的调用方式。

**step.assertions**: harness 根据故事叙述提取出的断言及其执行结果。

### 错误

| 状态码 | error.code | 场景 |
|--------|------------|------|
| 404 | `resource_not_found` | 运行不存在 |

---

## GET /api/v1/runs/{run_id}/stream

SSE（Server-Sent Events）实时流，用于 CLI 实时观看运行进度。

**响应**: `200 OK`，`Content-Type: text/event-stream`

### 事件类型

**run.started** — 运行开始执行

```
event: run.started
data: {"run_id":"run_p1q2r3","status":"running"}
```

**step.started** — 一个步骤开始执行

```
event: step.started
data: {"index":1,"chapter":"第一章 初来乍到","description":"注册用户叶知秋"}
```

**step.completed** — 一个步骤执行完��

```
event: step.completed
data: {"index":1,"status":"passed","duration_ms":340}
```

**step.log** — harness 输出的调试日志

```
event: step.log
data: {"index":1,"message":"POST /api/v1/users/register → 201 Created"}
```

**run.completed** — 运行执行完成

```
event: run.completed
data: {"run_id":"run_p1q2r3","status":"passed","step_summary":{"total":12,"passed":12,"failed":0},"duration_ms":15230}
```

**run.error** — 运行执行出错

```
event: run.error
data: {"run_id":"run_p1q2r3","status":"error","message":"harness 连接超时"}
```

### 错误

| 状态码 | error.code | 场景 |
|--------|------------|------|
| 404 | `resource_not_found` | 运行不存在 |
| 409 | `conflict` | 运行已结束，无可用流 |

---

## POST /api/v1/runs/{run_id}/cancel

取消一个正在排队或正在执行的运行。

**响应**: `200 OK`

```json
{
  "id": "run_p1q2r3",
  "status": "cancelled"
}
```

### 错误

| 状态码 | error.code | 场景 |
|--------|------------|------|
| 404 | `resource_not_found` | 运行不存在 |
| 409 | `conflict` | 运行已结束，无法取消 |

---

## POST /api/v1/runs/{run_id}/retry

以相同参数重新执行一个运行。创建一个新的 run。

**响应**: `202 Accepted`

返回新的 run 对象，格式同 `POST /api/v1/stories/{story_id}/runs` 的响应。

### 错误

| 状���码 | error.code | 场景 |
|--------|------------|------|
| 404 | `resource_not_found` | 运行不存在 |
