import React from 'react'
import ReactDOM from 'react-dom/client'
import './styles.css'

type Change = {
  rule_id: string
  type: string
  before: string
  after?: string | null
  reason: string
}

type Tip = {
  rule_id: string
  match: string
  message: string
  risk: string
}

type LineResult = {
  line_id: string
  index: number
  original_text: string
  suggested_text: string
  final_text: string
  changed: boolean
  changes: Change[]
  tips: Tip[]
  status: string
}

type ProcessResponse = {
  lines: LineResult[]
  final_text: string
}

type RuleOption = {
  rule_id: string
  name: string
  description: string
  action: string
  risk: string
}

const sampleText = [
  '随着人工智能技术的不断发展，越来越多的企业开始关注内容生产效率的提升。',
  '值得注意的是，AI 工具可以为企业提供帮助。',
  '总的来说，这种方式无疑具有重要意义。',
].join('\n')

function App() {
  const [input, setInput] = React.useState(sampleText)
  const [lines, setLines] = React.useState<LineResult[]>([])
  const [rules, setRules] = React.useState<RuleOption[]>([])
  const [enabledRuleIds, setEnabledRuleIds] = React.useState<string[]>([])
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState('')

  const finalText = lines.map((line) => line.final_text).join('\n')
  const allRulesEnabled = rules.length > 0 && enabledRuleIds.length === rules.length

  React.useEffect(() => {
    async function loadRules() {
      try {
        const response = await fetch('http://localhost:8000/api/rules')
        if (!response.ok) {
          throw new Error(`规则加载失败：${response.status}`)
        }
        const data = (await response.json()) as RuleOption[]
        setRules(data)
        setEnabledRuleIds(data.map((rule) => rule.rule_id))
      } catch (err) {
        setError(err instanceof Error ? err.message : '规则加载失败')
      }
    }

    loadRules()
  }, [])

  async function processArticle() {
    setLoading(true)
    setError('')
    try {
      const response = await fetch('http://localhost:8000/api/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: input, enabled_rule_ids: enabledRuleIds }),
      })
      if (!response.ok) {
        throw new Error(`请求失败：${response.status}`)
      }
      const data = (await response.json()) as ProcessResponse
      setLines(data.lines)
    } catch (err) {
      setError(err instanceof Error ? err.message : '处理失败')
    } finally {
      setLoading(false)
    }
  }

  function acceptLine(lineId: string) {
    setLines((current) =>
      current.map((line) =>
        line.line_id === lineId
          ? { ...line, final_text: line.suggested_text, status: 'accepted' }
          : line,
      ),
    )
  }

  function rejectLine(lineId: string) {
    setLines((current) =>
      current.map((line) =>
        line.line_id === lineId
          ? { ...line, final_text: line.original_text, status: 'rejected' }
          : line,
      ),
    )
  }

  function editLine(lineId: string, text: string) {
    setLines((current) =>
      current.map((line) =>
        line.line_id === lineId ? { ...line, final_text: text, status: 'edited' } : line,
      ),
    )
  }

  function acceptAll() {
    setLines((current) =>
      current.map((line) => ({ ...line, final_text: line.suggested_text, status: 'accepted' })),
    )
  }

  function resetAll() {
    setLines((current) =>
      current.map((line) => ({ ...line, final_text: line.original_text, status: 'processed' })),
    )
  }

  function toggleRule(ruleId: string) {
    setEnabledRuleIds((current) =>
      current.includes(ruleId) ? current.filter((item) => item !== ruleId) : [...current, ruleId],
    )
  }

  function toggleAllRules() {
    setEnabledRuleIds(allRulesEnabled ? [] : rules.map((rule) => rule.rule_id))
  }

  return (
    <main className="page">
      <section className="hero">
        <div>
          <p className="eyebrow">TextCheck MVP</p>
          <h1>AI 味逐行改写工具</h1>
          <p className="intro">按文章输入，后端按行拆分，用 jieba 字典命中规则，只做低风险自动修改。</p>
        </div>
        <div className="actions">
          <button onClick={processArticle} disabled={loading}>{loading ? '处理中...' : '开始处理'}</button>
          <button className="secondary" onClick={acceptAll} disabled={!lines.length}>全部接受</button>
          <button className="ghost" onClick={resetAll} disabled={!lines.length}>全部还原</button>
        </div>
      </section>

      {error && <div className="error">{error}</div>}

      <section className="panel rule-panel">
        <div className="rule-panel-head">
          <div>
            <h2>规则选择</h2>
            <p>当前启用 {enabledRuleIds.length} / {rules.length} 条规则。可以全部启用，也可以只跑单个规则验证效果。</p>
          </div>
          <button className="secondary" onClick={toggleAllRules} disabled={!rules.length}>
            {allRulesEnabled ? '全部取消' : '全部选择'}
          </button>
        </div>

        {!rules.length ? (
          <div className="empty compact">暂无可选规则。</div>
        ) : (
          <div className="rule-list">
            {rules.map((rule) => (
              <label className="rule-option" key={rule.rule_id}>
                <input
                  type="checkbox"
                  checked={enabledRuleIds.includes(rule.rule_id)}
                  onChange={() => toggleRule(rule.rule_id)}
                />
                <span>
                  <strong>{rule.rule_id}</strong>
                  <small>{rule.description}</small>
                </span>
              </label>
            ))}
          </div>
        )}
      </section>

      <section className="workspace">
        <div className="panel input-panel">
          <h2>原始文章</h2>
          <textarea value={input} onChange={(event) => setInput(event.target.value)} />
        </div>

        <div className="panel result-panel">
          <h2>逐行修改</h2>
          {!lines.length ? (
            <div className="empty">点击“开始处理”后查看每行结果。</div>
          ) : (
            <div className="line-list">
              {lines.map((line) => (
                <article className="line-card" key={line.line_id}>
                  <div className="line-head">
                    <span>第 {line.index + 1} 行</span>
                    <span className={`status ${line.status}`}>{line.status}</span>
                  </div>
                  <div className="compare-grid">
                    <div>
                      <label>修改前</label>
                      <p>{line.original_text}</p>
                    </div>
                    <div>
                      <label>建议修改</label>
                      <p className={line.changed ? 'changed' : ''}>{line.suggested_text}</p>
                    </div>
                  </div>

                  {!!line.changes.length && (
                    <div className="meta-list">
                      {line.changes.map((change, index) => (
                        <span key={`${line.line_id}-${change.rule_id}-${index}`}>
                          {change.reason}：{change.before}{change.after ? ` → ${change.after}` : ''}
                        </span>
                      ))}
                    </div>
                  )}

                  {!!line.tips.length && (
                    <div className="tips">
                      {line.tips.map((tip) => (
                        <span key={`${line.line_id}-${tip.rule_id}`}>提示：{tip.match}，{tip.message}</span>
                      ))}
                    </div>
                  )}

                  <textarea
                    className="line-edit"
                    value={line.final_text}
                    onChange={(event) => editLine(line.line_id, event.target.value)}
                  />

                  <div className="row-actions">
                    <button onClick={() => acceptLine(line.line_id)} disabled={!line.changed}>接受本行</button>
                    <button className="secondary" onClick={() => rejectLine(line.line_id)}>还原本行</button>
                  </div>
                </article>
              ))}
            </div>
          )}
        </div>
      </section>

      <section className="panel final-panel">
        <h2>最终文章</h2>
        <textarea readOnly value={finalText} placeholder="确认后的最终文本会显示在这里" />
      </section>
    </main>
  )
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
