---
name: test-story
description: >
  This skill should be used when the user asks to "run a test story",
  "execute story-driven tests", "test an API with a story file",
  "run story1.md", mentions "故事测试" or "故事驱动测试",
  asks to write or validate story-format test files,
  or references markdown files in a stories/ directory as test specifications.
version: 1.0.0
---

# Story-Driven API Testing

## Overview

Story-driven testing uses narrative markdown files to describe test scenarios. Instead of code-based test cases, tests are written as short stories where characters interact with a system. The narrative naturally embeds API calls, expected responses, and edge cases.

Claude acts as the test executor (harness): read the story, understand the implied operations, execute them via HTTP requests, and report results chapter by chapter.

For the story markdown format specification, see `references/story-format.md`. For a complete example, see `examples/story1.md`.

## Execution Procedure

### Step 1: Parse the Story

Read the markdown file and extract:

1. **Title** from the H1 heading
2. **Meta block** from the fenced code block tagged `meta` — extract `target` (base URL) and `scene` (default: `api`)
3. **Chapters** from H2 headings — skip chapters titled "楔子" (prologue) or "尾声" (epilogue)
4. **Paragraphs** within each chapter — each paragraph with substantive content is a test step

### Step 2: Discover the API

Before executing tests, discover the API structure of the target server:

```bash
curl -s "${TARGET}/openapi.json" 2>/dev/null || curl -s "${TARGET}/docs" 2>/dev/null || curl -s "${TARGET}/api/docs" 2>/dev/null || curl -s "${TARGET}/swagger.json" 2>/dev/null
```

If an OpenAPI/Swagger spec is found, use it to determine exact endpoints, request schemas, and authentication methods. If not found, infer RESTful endpoints from the narrative context and adapt based on actual responses.

Also verify the server is reachable:

```bash
curl -s -o /dev/null -w '%{http_code}' "${TARGET}/"
```

If the server is unreachable, report immediately and stop.

### Step 3: Extract Operations from Narrative

Read each paragraph and identify the implied HTTP operations. Common Chinese narrative patterns and their API mappings:

| Narrative Pattern | HTTP Operation |
|---|---|
| 注册 (register) with username/email/password | `POST /api/users` or `/api/register` |
| 登录 (login) | `POST /api/login` or `/api/auth/token` |
| 搜索 (search) keyword | `GET /api/search?q=...` or `/api/books?q=...` |
| 加到购物车 (add to cart) | `POST /api/cart/items` |
| 修改数量 (update quantity) | `PUT /api/cart/items/{id}` |
| 提交订单 (place order) | `POST /api/orders` |
| 支付 (pay) | `POST /api/orders/{id}/pay` or `/api/payments` |
| 查看 (view) resource | `GET /api/{resource}/{id}` |
| 删除 (delete) resource | `DELETE /api/{resource}/{id}` |

These are starting points — always prefer the OpenAPI spec if available. If a guessed endpoint returns 404, try common alternatives before marking as ERROR.

### Step 4: Execute Requests

Use `curl` for all HTTP requests:

```bash
curl -s -w '\n%{http_code}\n%{time_total}' \
  -X METHOD "${TARGET}/path" \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer ${TOKEN}" \
  -d '{"key": "value"}'
```

**State management across steps** — maintain a running context:
- Store authentication tokens from login responses; include as `Authorization: Bearer <token>` in subsequent requests
- Store resource IDs (user_id, cart_item_id, order_id) from creation responses for use in later steps
- Store cookies if the API uses session-based auth

**Important**: Extract concrete data values from the narrative text (usernames, emails, passwords, search terms, prices) and use them in requests exactly as written in the story.

### Step 5: Verify Responses

For each step, extract expected behavior from the narrative and verify against the actual response:

| Narrative Cue | Verification |
|---|---|
| "很顺利" / "成功" (success) | Status 200/201 |
| "系统拒绝了" (rejected) | Status 4xx |
| "没有提供有效的身份认证" (no auth) | Status 401 |
| "无权访问" (no permission) | Status 403 |
| "商品不存在" (not found) | Status 404 |
| "身份标记是'X'" (field equals X) | Response body field matches value |
| "密码没有被显示出来" (field absent) | Field not present in response |
| "总共N条结果" (count = N) | Array length or total field = N |
| "小计是X元" (subtotal = X) | Calculated value matches |
| "ORD-开头" (starts with prefix) | Field matches pattern `^ORD-` |
| "状态没有再变化" (idempotent) | Second call returns same state |
| "结果是空的" (empty result) | Empty array or empty response body |
| "没有报错" (no error) | Status 200, no error field |

### Step 6: Report Results

Report results chapter by chapter as execution proceeds. Format:

```
## 测试报告: <Story Title>
Target: <URL>

### <Chapter Title>
- [PASS] <step description> (HTTP <status>, <duration>s)
- [FAIL] <step description>
  Expected: <what the story describes>
  Actual: <what the server returned>
  Response: <abbreviated body>
- [ERROR] <step description>
  Error: <connection error or unexpected exception>

### 汇总
Total: N steps | Passed: X | Failed: Y | Errors: Z
Duration: <total>s
```

Report each chapter's results immediately after completing it, so the user sees progress in real time. Do not wait until all chapters are done.

## Writing Stories

When the user asks to write a new test story, follow the format in `references/story-format.md`:

1. Ask for the target API URL and the business flow to test
2. Create a narrative with a user character walking through the happy path
3. Add a tester character who checks edge cases, security boundaries, and error handling
4. Embed concrete test data (names, emails, prices, IDs) naturally in the narrative
5. Describe expected system behavior clearly in the prose

## Key Principles

- **Story is source of truth**: All test data, assertions, and expected behaviors come from the narrative
- **Discover before guessing**: Always try to find API docs before inferring endpoints
- **Maintain state**: Track tokens, IDs, and session data across steps within a story
- **Report incrementally**: Show results chapter by chapter, not all at once
- **Adapt on the fly**: If an endpoint returns unexpected results, read the response and adjust the approach before marking as failure
- **No hardcoded schemas**: The skill works with any REST API — the story defines what to test, not the skill
