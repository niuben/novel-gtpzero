# Rules

当前规则集从零开始逐条验证：有效果的规则保留入库，没有效果的规则删除。

每一类规则是一个独立 JSON 文件，直接放在当前 `rules/` 目录下。文件名就是分类名，例如 `filler.json` 的分类是 `filler`。

---

## 当前已加载规则

| rule_id | 类型 | 行为 | 说明 |
|---------|------|------|------|
| `delete_pos_adverb` | POS 词性规则 | delete | 使用 `jieba.posseg` 识别副词并删除；否定词本身保留，否定后的程度副词删除，例如 `不太对` 改为 `不对` |
| `delete_attributive_adjective` | POS 词性规则 | delete | 使用 `jieba.posseg` 识别形容词定语并随机删除一部分；只处理 `形容词 + 的`，不删除谓语形容词 |
| `delete_reveal_word` | 语义词表规则 | delete | 删除揭示词和揭示短语，例如 `原来`、`竟然`、`没想到`、`他突然意识到`，避免提前点破转折或真相 |
| `edit_logical_conjunction` | 语义词表规则 | replace/delete | 替换或删除显性逻辑连接词，例如 `然而` 改为 `但`、`因此` 改为 `所以`，删除 `而且`、`以及`、`只要……就` 中的连接成分 |

---

## 规则类型

### 删除类规则（action: delete）

直接删除匹配的内容。

```json
{
  "action": "delete",
  "reason": "删除填充短语",
  "items": ["值得注意的是", "不可否认的是"]
}
```

### 替换类规则（action: replace）

将匹配的文本替换为更简洁的表达。

```json
{
  "action": "replace",
  "reason": "压缩弱动词结构",
  "items": {
    "进行分析": "分析",
    "进行修改": "修改"
  }
}
```

### 提示类规则（action: suggest）

提示作者该处可能存在问题，建议修改。

```json
{
  "action": "suggest",
  "reason": "表达偏抽象，建议补充具体对象、动作或指标",
  "items": ["效率", "体验", "价值"]
}
```

### 正则规则（pattern_type: regex）

使用正则表达式进行模式匹配。

```json
{
  "action": "delete",
  "pattern_type": "regex",
  "reason": "删除模板化开头",
  "items": ["^随着.{2,30}?的(?:不断|快速|持续)?发展[，,]"]
}
```

---

## 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| `action` | 是 | `delete`（删除）、`replace`（替换）、`suggest`（提示） |
| `reason` | 是 | 规则说明，描述为什么要执行此操作 |
| `items` | 是 | 匹配项列表。`replace` 类型为键值对对象，其余为字符串数组 |
| `pattern_type` | 否 | 默认为 `literal`（字面匹配），正则匹配需显式指定 `regex` |
| `risk` | 否 | `delete`/`replace` 默认 `low`，`suggest` 默认 `medium`。高风险提示写 `"risk": "high"` |
| `novel_context` | 否 | 悬疑小说场景下的具体说明，帮助作者理解该规则在悬疑写作中的意义 |

---

## 扩展指南

新增同类规则时，直接追加到对应文件的 `items` 里。如果是全新的规则类别，新建 JSON 文件并遵循上述格式。
