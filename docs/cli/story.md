# test-story story

故事管理命令。故事是 markdown 格式的测试用例，以小说叙事的方式描述测试过程。

## story add

向故事集添加一个故事。

```bash
test-story story add <collection> <file> [files...]
```

```bash
# 添加单个故事
test-story story add v2.1-sprint3 stories/story1.md

# 批量添加
test-story story add v2.1-sprint3 stories/story1.md stories/story2.md stories/story3.md

# 通配符
test-story story add v2.1-sprint3 stories/*.md
```

输出示例：

```
Added 'stories/story1.md' → 叶知秋的书店奇遇 (story_x1y2z3)
```

## story list

列出故事集中的所有故事。

```bash
test-story story list <collection> [options]
```

| 选项 | 说明 |
|------|------|
| `--scene` | 按场景类型过滤 |

输出示例：

```
ID             TITLE                    SCENE   TARGET
story_x1y2z3   叶知秋的书店奇遇          api     http://localhost:8080
story_a4b5c6   管理员的日常巡检          api     http://localhost:8080
```

## story show

查看故事详情。加 `--content` 可输出完整 markdown 原文。

```bash
test-story story show <story-id> [options]
```

| 选项 | 说明 |
|------|------|
| `--content` | 输出完整 markdown 内容 |

输出示例（不加 --content）：

```
Title:      叶知秋的书店奇遇
ID:         story_x1y2z3
Collection: v2.1-sprint3 (coll_a1b2c3)
Scene:      api
Target:     http://localhost:8080
Created:    2026-03-28 10:01:00
Updated:    2026-03-28 10:01:00
```

## story update

替换故事的 markdown 内容。

```bash
test-story story update <story-id> <file>
```

```bash
test-story story update story_x1y2z3 stories/story1_v2.md
```

## story remove

删除故事。

```bash
test-story story remove <story-id> [options]
```

| 选项 | 说明 |
|------|------|
| `--cascade` | 同时删除关联的运行记录 |

```bash
test-story story remove story_x1y2z3
test-story story remove story_x1y2z3 --cascade
```
