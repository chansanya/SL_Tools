interface Props {
  onRestoreLatest: () => void
  onRestoreInit: () => void
  onRefresh: () => void
}

export default function ActionBar({
  onRestoreLatest,
  onRestoreInit,
  onRefresh
}: Props): JSX.Element {
  return (
    <div className="row">
      <button className="btn btn-flame" onClick={onRestoreLatest}>
        回档至最新
      </button>
      <button className="btn btn-flame" onClick={onRestoreInit}>
        回档至初始
      </button>
      <div className="grow" />
      <button className="btn btn-ghost" onClick={onRefresh}>
        刷新
      </button>
    </div>
  )
}
