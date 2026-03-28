# test-story run

执行故事并查看运行结果。这是框架最核心的命令。

## run（快捷执行）

直接执行一个故事文件。这是最常用的方式，一条命令完成上传和执行。

```bash
test-story run <file> [options]
```

| 选项 | 说明 |
|------|------|
| `--target` | 覆盖测试目标地址 |
| `--harness` | 覆盖 harness |
| `--collection` | 将故事归入指定故事集 |
| `--env` | 环境变量，格式 `KEY=VALUE`，可多次使用 |
| `--no-stream` | 不实时输出，只返回 run ID |

```bash
# 最简用法——执行一个故事
test-story run stories/story1.md

# 指定目标和 harness
test-story run stories/story1.md --target http://staging:8080 --harness claude-agent-sdk

# 传入环境变量
test-story run stories/story1.md --env AUTH_TOKEN=test-token --env ADMIN_KEY=xxx

# 归入故事集
test-story run stories/story1.md --collection v2.1-sprint3

# 只提交不等待
test-story run stories/story1.md --no-stream
```

输出示例（实时流，默认行为）：

```
Story: 叶知秋的书店奇遇 (story_x1y2z3)
Run:   run_p1q2r3
Target: http://localhost:8080
Harness: claude-code → anthropic-main

第一章 初来乍到
  ✓ 注册用户叶知秋 (340ms)
  ✓ 重复注册，预期被拒绝 (210ms)
  ✓ 缺少邮箱注册，预期校验失败 (185ms)

第二章 寻找一本书
  ✓ 搜索"三体" (520ms)
  ✓ 搜索不存在的关键词，预期空结果 (190ms)
  ✓ 超大页码搜索，预期空结果 (200ms)

第三章 放进购物车
  ✓ 添加 2 本《三体》到购物车 (310ms)
  ✓ 修改数量为 1 (180ms)
  ✓ 数量设为 0，预期校验失败 (150ms)
  ✓ 不存在的书籍编号，预期商品不存在 (170ms)

第四章 下单
  ✓ 提交订单 (450ms)
  ✓ 支付前查询订单状态 (120ms)

第五章 付款
  ✓ 支付宝支付 (380ms)
  ✓ 重复支付通知，验证幂等性 (200ms)

第六章 不速之客
  ✓ 未认证访问订单，预期 401 (90ms)
  ✓ 越权访问订单，预期 403 (95ms)
  ✓ 伪造书籍编号加购物车，预期 404 (110ms)

PASSED  17/17 steps  4.3s
```

输出示例（有失败）：

```
...
第三章 放进购物车
  ✓ 添加 2 本《三体》到购物车 (310ms)
  ✗ 修改数量为 1 (180ms)
    Expected: 小计变为 36.80 元
    Actual:   小计仍为 73.60 元

...

FAILED  11/17 steps passed, 1 failed  3.8s
```

## run exec

执行一个已存在于服务器上的故事。

```bash
test-story run exec <story-id> [options]
```

选项同 `test-story run`（除 `--collection` 外）。

```bash
test-story run exec story_x1y2z3
test-story run exec story_x1y2z3 --target http://staging:8080
```

## run list

列出运行记录。

```bash
test-story run list [options]
```

| 选项 | 说明 |
|------|------|
| `--story` | 按故事 ID 过滤 |
| `--collection` | 按故事集过滤 |
| `--batch` | 按批次 ID 过滤 |
| `--status` | 按状态过滤：`queued`、`running`、`passed`、`failed`、`error`、`cancelled` |

输出示例：

```
RUN ID        STORY                    STATUS   STEPS      DURATION   CREATED
run_p1q2r3    叶知秋的书店奇遇          passed   17/17      4.3s       10:05
run_s4t5u6    管理员的日常巡检          failed   8/12       3.1s       10:06
run_v7w8x9    叶知秋的书店奇遇          running  3/17       -          10:10
```

## run show

查看单次运行的详细结果。

```bash
test-story run show <run-id> [options]
```

| 选项 | 说明 |
|------|------|
| `--steps` | 展开显示所有步骤详情 |
| `--failed` | 只显示失败的步骤 |

输出示例（默认）：

```
Run:      run_p1q2r3
Story:    叶知秋的书店奇遇 (story_x1y2z3)
Status:   passed
Harness:  claude-code
Target:   http://localhost:8080
Steps:    17/17 passed
Duration: 4.3s
Created:  2026-03-28 10:05:00
Finished: 2026-03-28 10:05:04

STEPS:
  #    CHAPTER              DESCRIPTION                          STATUS   DURATION
  1    第一章 初来乍到       注册用户叶知秋                        passed   340ms
  2    第一章 初来乍到       重复注册，预期被拒绝                    passed   210ms
  3    第一章 初来乍到       缺少邮箱注册，预期校验失败              passed   185ms
  ...
```

输出示例（--failed）：

```
FAILED STEPS:

  Step #8 — 第三章 放进购物车 — 修改数量为 1

  Narrative:
    叶知秋把数量从2改成了1。小计相应变成了36.80元。

  Request:
    PATCH /api/v1/cart/items/cart_001  →  200 OK

  Assertions:
    ✓ 数量变为 1
    ✗ 小计变为 36.80 元
      Expected: 36.80
      Actual:   73.60
```

## run cancel

取消一个正在排队或运行中的执行。

```bash
test-story run cancel <run-id>
```

```bash
test-story run cancel run_v7w8x9
# Run run_v7w8x9 cancelled.
```

## run retry

用相同参数重新执行一个运行。

```bash
test-story run retry <run-id>
```

```bash
test-story run retry run_s4t5u6
# New run run_j1k2l3 created. Streaming...
```

默认实时输出进度。加 `--no-stream` 只返回新的 run ID。
