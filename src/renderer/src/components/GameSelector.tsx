import { Select } from 'antd'
import type { GameConfig } from '../../../shared/types'

interface Props {
  games: Record<string, GameConfig>
  value: string
  onChange: (key: string) => void
}

export default function GameSelector({ games, value, onChange }: Props): JSX.Element {
  return (
    <Select
      value={value}
      onChange={onChange}
      style={{ width: 200 }}
      options={Object.entries(games).map(([key, g]) => ({ value: key, label: g.name }))}
    />
  )
}
