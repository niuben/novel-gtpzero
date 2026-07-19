# Rules

每一类规则是一个独立 JSON 文件，直接放在当前 `rules/` 目录下。文件名就是分类名，例如 `filler.json` 的分类是 `filler`。

本规则集特别针对**悬疑小说**场景进行了扩充，每条规则都包含了 `novel_context` 字段，说明该规则在悬疑写作中的具体意义。

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

## 规则文件清单

| 文件名 | 类别 | 类型 | 风险 |
|--------|------|------|------|
| `rule_of_three.json` | 三段式列举 | suggest/regex | high |
| `filler.json` | 填充短语 | delete | high |
| `wordy_expression.json` | 绕圈表达 | replace | — |
| `weak_verb.json` | 弱动词结构 | replace | — |
| `vague_subject.json` | 模糊主语 | suggest | high |
| `vague_authority.json` | 模糊权威 | suggest | high |
| `template_opening.json` | 模板化开头 | delete/regex | high |
| `surface_analysis.json` | 表面分析 | suggest/regex | high |
| `promo_language.json` | 宣传语言 | suggest | — |
| `parallel_structure.json` | 平行结构 | suggest/regex | medium |
| `negative_parallel.json` | 否定式排比 | suggest/regex | medium |
| `fake_range.json` | 假范围 | suggest/regex | medium |
| `empty_ending.json` | 空洞结尾 | suggest | high |
| `chat_artifact.json` | 聊天痕迹 | delete | high |
| `ai_vocabulary.json` | AI高频词汇 | suggest | high |
| `ai_disclaimer.json` | AI免责声明 | suggest | high |
| `abstract_expression.json` | 抽象表达 | suggest | — |
| `absolute_tone.json` | 绝对语气 | suggest | — |

---

## 悬疑小说写作核心原则

1. **具体胜于抽象**：能用感官（视觉、听觉、触觉、嗅觉）描写的，不用概念词
2. **动词胜于形容词**：让动作说话，不要用形容词替读者感受
3. **断裂胜于工整**：不对称的节奏比整齐的排比更有紧张感
4. **沉默胜于解释**：不要替读者分析"这意味着什么"
5. **不确定胜于确定**：悬疑的核心是张力，绝对语气会毁掉张力

---

## 扩展指南

新增同类规则时，直接追加到对应文件的 `items` 里。如果是全新的规则类别，新建 JSON 文件并遵循上述格式。

对于悬疑小说的规则扩展，建议同时补充 `novel_context` 字段，说明该规则在悬疑场景下的具体考量。
