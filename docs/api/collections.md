# 故事集（Collections）

故事集是一批相关故事的集合，通常与软件迭代周期对应。例如 `v2.1-sprint3` 故事集包含该迭代需要验证的所有故事。

## POST /api/v1/collections

创建故事集。

**请求**:

```json
{
  "name": "v2.1-sprint3",
  "description": "2.1 版本第三个迭代的回归测试",
  "target": "http://localhost:8080",
  "harness": "claude-code"
}
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | string | 是 | 故事集名称，需唯一 |
| `description` | string | 否 | 描述 |
| `target` | string | 否 | 默认测试目标地址，故事级和运行级可覆盖 |
| `harness` | string | 否 | 默认 harness，故事级和运行级可覆盖 |

**响应**: `201 Created`

```json
{
  "id": "coll_a1b2c3",
  "name": "v2.1-sprint3",
  "description": "2.1 版本第三个迭代的回归测试",
  "target": "http://localhost:8080",
  "harness": "claude-code",
  "story_count": 0,
  "created_at": "2026-03-28T10:00:00Z",
  "updated_at": "2026-03-28T10:00:00Z"
}
```

### 错误

| 状态码 | error.code | 场景 |
|--------|------------|------|
| 400 | `validation_error` | name 为空 |
| 409 | `conflict` | 同名故事集已存在 |

---

## GET /api/v1/collections

列出所有故事集。

**查询参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| `page` | integer | 页码 |
| `per_page` | integer | 每页条数 |

**响应**: `200 OK`

```json
{
  "items": [
    {
      "id": "coll_a1b2c3",
      "name": "v2.1-sprint3",
      "description": "2.1 版本第三个迭代的回归测试",
      "target": "http://localhost:8080",
      "harness": "claude-code",
      "story_count": 3,
      "created_at": "2026-03-28T10:00:00Z",
      "updated_at": "2026-03-28T10:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 20
}
```

---

## GET /api/v1/collections/{collection_id}

获取单个故事集的详情。

**响应**: `200 OK`

```json
{
  "id": "coll_a1b2c3",
  "name": "v2.1-sprint3",
  "description": "2.1 版本第三个迭代的回归测试",
  "target": "http://localhost:8080",
  "harness": "claude-code",
  "story_count": 3,
  "stories": [
    {
      "id": "story_x1y2z3",
      "title": "叶知秋的书店奇遇",
      "scene": "api"
    }
  ],
  "created_at": "2026-03-28T10:00:00Z",
  "updated_at": "2026-03-28T10:00:00Z"
}
```

### 错误

| 状态码 | error.code | 场景 |
|--------|------------|------|
| 404 | `resource_not_found` | 故事集不存在 |

---

## PATCH /api/v1/collections/{collection_id}

更新故事集信息。只需传入要修改的字段。

**请求**:

```json
{
  "name": "v2.1-sprint3-hotfix",
  "target": "http://staging:8080"
}
```

**响应**: `200 OK`

返回更新后的完整故事集对象。

### 错误

| 状态码 | error.code | 场景 |
|--------|------------|------|
| 404 | `resource_not_found` | 故事集不存在 |
| 409 | `conflict` | 新名称与已有故事集冲突 |

---

## DELETE /api/v1/collections/{collection_id}

删除故事集。

**查询参数**:

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `cascade` | boolean | false | 是否同时删除集合内的所有故事及其运行记录 |

**响应**: `204 No Content`

### 错误

| 状态码 | error.code | 场景 |
|--------|------------|------|
| 404 | `resource_not_found` | 故事集不存在 |
| 409 | `conflict` | 故事集内仍有故事且未设置 cascade=true |

---

## POST /api/v1/collections/{collection_id}/runs

执行整个故事集。为集合内每个故事创建一个 run，返回一个批次（batch）。

**请求（可选覆盖）**:

```json
{
  "target": "http://staging:8080",
  "harness": "claude-agent-sdk"
}
```

**响应**: `202 Accepted`

```json
{
  "batch_id": "batch_m1n2o3",
  "collection_id": "coll_a1b2c3",
  "status": "queued",
  "runs": [
    {
      "id": "run_p1q2r3",
      "story_id": "story_x1y2z3",
      "story_title": "叶知秋的书店奇遇",
      "status": "queued"
    }
  ],
  "total_stories": 3,
  "created_at": "2026-03-28T10:05:00Z"
}
```

### 错误

| 状态码 | error.code | 场景 |
|--------|------------|------|
| 404 | `resource_not_found` | 故事集不存在 |
| 409 | `conflict` | 故事集为空，没有可执行的故事 |
