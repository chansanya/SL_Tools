interface Props {
  name: string
  setName: (v: string) => void
  onCreate: () => void
  busy: boolean
}

/** 存档名输入 + 存档按钮; 回车提交 */
export default function ArchiveForm({ name, setName, onCreate, busy }: Props): JSX.Element {
  return (
    <div className="card row">
      <span className="label">存档名</span>
      <input
        className="input"
        value={name}
        onChange={(e) => setName(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter') onCreate()
        }}
        placeholder="留空则用时间戳自动命名"
      />
      <button className="btn btn-primary" onClick={onCreate} disabled={busy}>
        {busy ? '处理中…' : '存档'}
      </button>
    </div>
  )
}
