import type { GameConfig } from '../../../shared/types'

interface Props {
  games: Record<string, GameConfig>
  value: string
  onChange: (key: string) => void
}

export default function GameSelector({ games, value, onChange }: Props): JSX.Element {
  return (
    <div className="row">
      <span className="label">选择游戏</span>
      <select className="select" value={value} onChange={(e) => onChange(e.target.value)}>
        {Object.entries(games).map(([key, g]) => (
          <option key={key} value={key}>
            {g.name}
          </option>
        ))}
      </select>
    </div>
  )
}
