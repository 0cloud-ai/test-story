# 故事（Stories）

故事是 markdown 格式的测试用例，以小说叙事的方式描述测试工程师的手工测试过程。每个故事归属于一个故事集。

故事文件顶部包含一个 `meta` 块，声明测试目标和场景类型：

```markdown
# 故事标题

​```meta
target: http://localhost:8080
scene: api
​```
```

服务器从 `meta` 块提取 `target` 和 `scene`，从第一个 H1 标题提取 `title`。

## POST /api/v1/collections/{collection_id}/stories

向故事集添加一个故事。请求体为 markdown 原文。

**请求**: `Content-Type: text/markdown`

```markdown
# 叶知秋的书店奇遇

​```meta
target: http://localhost:8080
scene: api
​```

## 楔子

陆青是拾光书店项目组的测试工程师...
```

**响应**: `201 Created`

```json
{
  "id": "story_x1y2z3",
  "collection_id": "coll_a1b2c3",
  "title": "叶知秋的书店奇遇",
  "scene": "api",
  "target": "http://localhost:8080",
  "created_at": "2026-03-28T10:01:00Z",
  "updated_at": "2026-03-28T10:01:00Z"
}
```

### 错误

| 状态码 | error.code | 场景 |
|--------|------------|------|
| 404 | `resource_not_found` | 故事集��存在 |
| 422 | `unprocessable` | 故事缺少 meta 块或 meta 块格式不正确 |
| 422 | `unprocessable` | scene 值不在支持的场景列表中 |

---

## GET /api/v1/collections/{collection_id}/stories

列出故事集中的所有故事。

**查询���数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| `scene` | string | 按场景类型过滤，如 `api` |
| `page` | integer | 页码 |
| `per_page` | integer | 每页条数 |

**响应**: `200 OK`

```json
{
  "items": [
    {
      "id": "story_x1y2z3",
      "collection_id": "coll_a1b2c3",
      "title": "叶知秋的书店奇遇",
      "scene": "api",
      "target": "http://localhost:8080",
      "created_at": "2026-03-28T10:01:00Z",
      "updated_at": "2026-03-28T10:01:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 20
}
```

### 错误

| 状态码 | error.code | 场景 |
|--------|------------|------|
| 404 | `resource_not_found` | 故事集���存在 |

---

## GET /api/v1/stories/{story_id}

获取单个故事的详情，包含完整的 markdown 原文。

**响应**: `200 OK`

```json
{
  "id": "story_x1y2z3",
  "collection_id": "coll_a1b2c3",
  "title": "叶知秋的书店奇遇",
  "scene": "api",
  "target": "http://localhost:8080",
  "content": "# 叶知秋的书店奇遇\n\n```meta\ntarget: http://localhost:8080\nscene: api\n```\n\n## 楔子\n\n陆青是拾��书店项目组的测试工程师...",
  "created_at": "2026-03-28T10:01:00Z",
  "updated_at": "2026-03-28T10:01:00Z"
}
```

### 错误

| 状态码 | error.code | 场景 |
|--------|------------|------|
| 404 | `resource_not_found` | 故事不存在 |

---

## PUT /api/v1/stories/{story_id}

替换故事的 markdown 内容。服务器重新解析 meta 块和标题。

**请求**: `Content-Type: text/markdown`

完整的 markdown 原文（同创建时的格式）��

**响应**: `200 OK`

返��更新后的故事对象（同 `GET /api/v1/stories/{story_id}`，但不含 `content` 字段）。

### 错误

| 状态码 | error.code | 场景 |
|--------|------------|------|
| 404 | `resource_not_found` | 故事不存在 |
| 422 | `unprocessable` | 新内容缺少 meta 块或格式不正确 |

---

## DELETE /api/v1/stories/{story_id}

删除故事。

**查询参数**:

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `cascade` | boolean | false | 是否同时删除关联的运行记录 |

**响应**: `204 No Content`

### 错误

| 状态码 | error.code | 场景 |
|--------|------------|------|
| 404 | `resource_not_found` | 故事不存在 |
