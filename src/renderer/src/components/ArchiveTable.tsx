import type { ArchiveInfo } from '../../../shared/types'
import { formatTime } from '../utils'

interface Props {
  archives: ArchiveInfo[]
  onOpen: (a: ArchiveInfo) => void
  onRestore: (a: ArchiveInfo) => void
  onDelete: (a: ArchiveInfo) => void
}

export default function ArchiveTable({ archives, onOpen, onRestore, onDelete }: Props): JSX.Element {
  return (
    <div className="table-wrap card">
      <table className="table">
        <thead>
          <tr>
            <th>存档名</th>
            <th className="th-time">创建时间</th>
            <th className="th-op">操作</th>
          </tr>
        </thead>
        <tbody>
          {archives.length === 0 ? (
            <tr>
              <td colSpan={3} className="empty">
                暂无存档
              </td>
            </tr>
          ) : (
            archives.map((a) => (
              <tr key={a.path}>
                <td className="td-name">{a.name}</td>
                <td className="td-time">{formatTime(a.ctime)}</td>
                <td className="td-op">
                  <button className="btn btn-ghost btn-sm" onClick={() => onOpen(a)}>
                    打开
                  </button>
                  <button className="btn btn-sm" onClick={() => onRestore(a)}>
                    回档
                  </button>
                  <button className="btn btn-danger btn-sm" onClick={() => onDelete(a)}>
                    删除
                  </button>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}
