import { useCallback, useEffect, useState } from 'react'
import { App as AntApp, Button, Input, Space, Typography } from 'antd'
import type { ArchiveInfo, SLConfig, SwitchGameResult } from '../../shared/types'
import GameSelector from './components/GameSelector'
import ArchiveTable from './components/ArchiveTable'
import TitleBar from './components/TitleBar'

const { Text } = Typography

export default function App(): JSX.Element {
  const [config, setConfig] = useState<SLConfig | null>(null)
  const [gameKey, setGameKey] = useState('')
  const [switched, setSwitched] = useState<SwitchGameResult | null>(null)
  const [sourceDir, setSourceDir] = useState('')
  const [archives, setArchives] = useState<ArchiveInfo[]>([])
  const [name, setName] = useState('')
  const [busy, setBusy] = useState(false)

  const { message, modal } = AntApp.useApp()

  const refresh = useCallback(async (): Promise<void> => {
    if (!gameKey) return
    try {
      setArchives(await window.api.listArchives(gameKey))
    } catch (e) {
      message.error(String(e))
    }
  }, [gameKey, message])

  useEffect(() => {
    window.api
      .getConfig()
      .then((cfg) => {
        setConfig(cfg)
        const first = Object.keys(cfg.games)[0]
        if (first) setGameKey(first)
      })
      .catch((e) => message.error(String(e)))
  }, [message])

  useEffect(() => {
    if (!gameKey) return
    let cancelled = false
    window.api
      .switchGame(gameKey)
      .then((r) => {
        if (cancelled) return
        setSwitched(r)
        setSourceDir(r.sourceDir)
        if (r.createdDefault) message.success(`已生成《${r.gameName}》初始默认备份`)
      })
      .then(() => refresh())
      .catch((e) => message.error(String(e)))
    return () => {
      cancelled = true
    }
  }, [gameKey, refresh, message])

  useEffect(() => {
    if (!config) return
    const id = setInterval(() => refresh(), config.app.table_refresh)
    return () => clearInterval(id)
  }, [config, refresh])

  const confirmDialog = (title: string, content: string): Promise<boolean> =>
    new Promise((resolve) => {
      modal.confirm({
        title,
        content,
        okText: '确定',
        cancelText: '取消',
        onOk: () => resolve(true),
        onCancel: () => resolve(false)
      })
    })

  const handlePickSource = async (): Promise<void> => {
    const p = await window.api.pickSource()
    if (p) {
      setSourceDir(p)
      message.success('源目录已更新(本次会话生效)')
    }
  }

  const handleCreate = async (): Promise<void> => {
    if (busy) return
    setBusy(true)
    try {
      await window.api.createArchive(gameKey, name, sourceDir)
      setName('')
      message.success('存档成功')
      await refresh()
    } catch (e) {
      message.error(String(e))
    } finally {
      setBusy(false)
    }
  }

  const handleRestore = async (a: ArchiveInfo): Promise<void> => {
    const ok = await confirmDialog('确认回档', `将回档至《${a.name}》, 当前源目录文件会被覆盖, 继续?`)
    if (!ok) return
    try {
      await window.api.restoreArchive(gameKey, a.path, sourceDir)
      message.success(`回档《${a.name}》成功`)
      await refresh()
    } catch (e) {
      message.error(String(e))
    }
  }

  const handleDelete = async (a: ArchiveInfo): Promise<void> => {
    const def = a.fileName.endsWith('默认备份.zip')
    const ok = await confirmDialog(
      def ? '删除默认存档' : '删除存档',
      def
        ? `《${a.name}》是默认存档, 删除后将无法恢复初始存档, 确定?`
        : `确认删除《${a.name}》?`
    )
    if (!ok) return
    try {
      await window.api.deleteArchive(gameKey, a.path)
      message.success('删除成功')
      await refresh()
    } catch (e) {
      message.error(String(e))
    }
  }

  const handleRestoreLatest = async (): Promise<void> => {
    if (archives.length === 0) {
      message.info('暂无存档')
      return
    }
    await handleRestore(archives[0])
  }

  const handleRestoreInit = async (): Promise<void> => {
    if (!switched) return
    const init = archives.find((a) => a.name === `${switched.gameName}默认备份`)
    if (!init) {
      message.error('未找到初始默认存档')
      return
    }
    await handleRestore(init)
  }

  const handleOpen = async (p: string): Promise<void> => {
    try {
      await window.api.openPath(p)
    } catch (e) {
      message.error(String(e))
    }
  }

  if (!config) {
    return (
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100%',
          color: '#9aa3b2'
        }}
      >
        加载中…
      </div>
    )
  }

  return (
    <div className="app">
      <TitleBar />
      <header className="app-header">
        <div className="current-game">{switched?.gameName ?? '—'}</div>
        <GameSelector games={config.games} value={gameKey} onChange={setGameKey} />
      </header>

      <main className="app-main">
        <div className="card-row">
          <Text type="secondary">源存档目录</Text>
          <Space.Compact style={{ flex: 1 }}>
            <Input value={sourceDir} readOnly />
            <Button onClick={handlePickSource}>重新选择</Button>
            <Button onClick={() => handleOpen(sourceDir)}>打开</Button>
          </Space.Compact>
        </div>

        <div className="card-row">
          <Text type="secondary">存档名</Text>
          <Space.Compact style={{ flex: 1 }}>
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              onPressEnter={handleCreate}
              placeholder="留空则用时间戳自动命名"
            />
            <Button type="primary" onClick={handleCreate} loading={busy}>
              存档
            </Button>
          </Space.Compact>
        </div>

        <Space>
          <Button type="primary" ghost onClick={handleRestoreLatest}>
            回档至最新
          </Button>
          <Button type="primary" ghost onClick={handleRestoreInit}>
            回档至初始
          </Button>
          <Button onClick={refresh}>刷新</Button>
        </Space>

        <div>
          <Text type="secondary">最新存档 </Text>
          <Text strong style={{ color: '#4f8cff' }}>
            {archives[0]?.name ?? '—'}
          </Text>
        </div>

        <ArchiveTable
          archives={archives}
          onOpen={(a) => handleOpen(a.path)}
          onRestore={handleRestore}
          onDelete={handleDelete}
        />
      </main>
    </div>
  )
}
