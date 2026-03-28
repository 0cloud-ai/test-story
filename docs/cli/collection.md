# test-story collection

故事集管理命令。故事集是一批相关故事的集合，通常与软件迭代周期对应。

## collection create

创建故事集。

```bash
test-story collection create <name> [options]
```

| 选项 | 说明 |
|------|------|
| `--description` | 描述 |
| `--target` | 默认测试目标地址 |
| `--harness` | 默认 harness |

```bash
test-story collection create v2.1-sprint3 \
  --description "2.1 版本第三个迭代的回归测试" \
  --target http://localhost:8080

test-story collection create hotfix-20260328
```

## collection list

列出所有故事集。

```bash
test-story collection list
```

输出示例：

```
NAME              STORIES   TARGET                    CREATED
v2.1-sprint3      3         http://localhost:8080      2026-03-28 10:00
hotfix-20260328   1         -                         2026-03-28 14:00
```

## collection show

查看故事集详情，包含其中的故事列表。

```bash
test-story collection show <name-or-id>
```

输出示例：

```
Name:        v2.1-sprint3
ID:          coll_a1b2c3
Description: 2.1 版本第三个迭代的回归测试
Target:      http://localhost:8080
Harness:     claude-code
Stories:     3
Created:     2026-03-28 10:00:00

STORIES:
  #   TITLE                    SCENE
  1   叶知秋的书店奇遇          api
  2   管理员的日常巡检          api
  3   恶意用户的渗透测试        api
```

## collection update

更新故事集信息。

```bash
test-story collection update <name-or-id> [options]
```

| 选项 | 说明 |
|------|------|
| `--name` | 新名称 |
| `--description` | 新描述 |
| `--target` | 新测试目标地址 |
| `--harness` | 新 harness |

```bash
test-story collection update v2.1-sprint3 --target http://staging:8080
```

## collection remove

删除故事集。

```bash
test-story collection remove <name-or-id> [options]
```

| 选项 | 说明 |
|------|------|
| `--cascade` | 同时删除集合内所有故事及其运行记录 |

```bash
# 删除空故事集
test-story collection remove hotfix-20260328

# 级联删除
test-story collection remove v2.1-sprint3 --cascade
```

## collection run

执行整个故事集中的所有故事。

```bash
test-story collection run <name-or-id> [options]
```

| 选项 | 说明 |
|------|------|
| `--target` | 覆盖测试目标地址 |
| `--harness` | 覆盖 harness |
| `--no-stream` | 不实时输出，只返回批次 ID |

```bash
# 执行并实时查看进度
test-story collection run v2.1-sprint3

# 覆盖目标地址
test-story collection run v2.1-sprint3 --target http://staging:8080

# 只提交不等待
test-story collection run v2.1-sprint3 --no-stream
```

输出示例（实时流）：

```
Batch batch_m1n2o3 started — 3 stories

[1/3] 叶知秋的书店奇遇
  ✓ 第一章 初来乍到 — 注册用户叶知秋 (340ms)
  ✓ 第一章 初来乍到 — 重复注册，预期被拒绝 (210ms)
  ✓ 第一章 初来乍到 — 缺少邮箱注册，预期校验失败 (185ms)
  ✓ 第二章 寻找一本书 — 搜索"三体" (520ms)
  ...
  ✓ PASSED (12/12 steps, 15.2s)

[2/3] 管理员的日常巡检
  ✓ 第一章 ...
  ...

[3/3] 恶意用户的渗透测试
  ...

Batch complete: 3 passed, 0 failed
```
