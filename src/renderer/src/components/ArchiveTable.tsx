import { Button, Card, Space, Table, type TableProps } from 'antd'
import type { ArchiveInfo } from '../../../shared/types'
import { formatTime } from '../utils'

interface Props {
  archives: ArchiveInfo[]
  onOpen: (a: ArchiveInfo) => void
  onRestore: (a: ArchiveInfo) => void
  onDelete: (a: ArchiveInfo) => void
}

export default function ArchiveTable({ archives, onOpen, onRestore, onDelete }: Props): JSX.Element {
  const columns: TableProps<ArchiveInfo>['columns'] = [
    { title: '存档名', dataIndex: 'name', key: 'name' },
    {
      title: '创建时间',
      dataIndex: 'ctime',
      key: 'ctime',
      width: 170,
      render: (v: number) => formatTime(v)
    },
    {
      title: '操作',
      key: 'op',
      width: 210,
      render: (_, a) => (
        <Space size="small">
          <Button size="small" onClick={() => onOpen(a)}>
            打开
          </Button>
          <Button size="small" type="primary" ghost onClick={() => onRestore(a)}>
            回档
          </Button>
          <Button size="small" danger onClick={() => onDelete(a)}>
            删除
          </Button>
        </Space>
      )
    }
  ]

  return (
    <Card className="table-card" size="small">
      <Table
        size="small"
        dataSource={archives}
        columns={columns}
        rowKey="path"
        pagination={false}
        locale={{ emptyText: '暂无存档' }}
      />
    </Card>
  )
}
