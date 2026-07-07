interface Props {
  name: string
}

export default function LatestArchive({ name }: Props): JSX.Element {
  return (
    <div className="latest row">
      <span className="label">最新存档</span>
      <span className="latest-name">{name || '—'}</span>
    </div>
  )
}
