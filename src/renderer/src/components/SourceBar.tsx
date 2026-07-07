interface Props {
  sourceDir: string
  onPick: () => void
  onOpen: () => void
}

/** 源存档目录: 只读展示 + 重新选择(本次会话生效) + 打开 */
export default function SourceBar({ sourceDir, onPick, onOpen }: Props): JSX.Element {
  return (
    <div className="card row">
      <span className="label">源存档目录</span>
      <input className="input" value={sourceDir} readOnly placeholder="未选择" />
      <button className="btn btn-ghost btn-sm" onClick={onPick}>
        重新选择
      </button>
      <button className="btn btn-ghost btn-sm" onClick={onOpen}>
        打开
      </button>
    </div>
  )
}
