import { useCallback, useEffect, useRef, useState } from 'react'
import type { ArchiveInfo, SLConfig, SwitchGameResult } from '../../shared/types'
import GameSelector from './components/GameSelector'
import SourceBar from './components/SourceBar'
import ArchiveForm from './components/ArchiveForm'
import ActionBar from './components/ActionBar'
import LatestArchive from './components/LatestArchive'
import ArchiveTable from './components/ArchiveTable'
import ConfirmDialog, { type ConfirmHandle } from './components/ConfirmDialog'
import Toast, { type ToastHandle } from './components/Toast'
import TitleBar from './components/TitleBar'

type ToastKind = 'info' | 'success' | 'error'

export default function App(): JSX.Element {
  const [config, setConfig] = useState<SLConfig | null>(null)
  const [gameKey, setGameKey] = useState('')
  const [switched, setSwitched] = useState<SwitchGameResult | null>(null)
  const [sourceDir, setSourceDir] = useState('')
  const [archives, setArchives] = useState<ArchiveInfo[]>([])
  const [name, setName] = useState('')
  const [busy, setBusy] = useState(false)

  const confirmRef = useRef<ConfirmHandle>(null)
  const toastRef = useRef<ToastHandle>(null)

  const toast = (text: string, kind: ToastKind = 'info'): void => {
    toastRef.current?.show(text, kind)
  }
  const confirm = (title: string, message: string): Promise<boolean> =>
    confirmRef.current?.ask(title, message) ?? Promise.resolve(false)

  const refresh = useCallback(async (): Promise<void> => {
    if (!gameKey) return
    try {
      setArchives(await window.api.listArchives(gameKey))
    } catch (e) {
      toast(String(e), 'error')
    }
  }, [gameKey])

  // 加载配置, 默认选首个游戏
  useEffect(() => {
    window.api
      .getConfig()
      .then((cfg) => {
        setConfig(cfg)
        const first = Object.keys(cfg.games)[0]
        if (first) setGameKey(first)
      })
      .catch((e) => toast(String(e), 'error'))
  }, [])

  // 切换游戏: 触发默认备份自检 + 刷新列表
  useEffect(() => {
    if (!gameKey) return
    let cancelled = false
    window.api
      .switchGame(gameKey)
      .then((r) => {
        if (cancelled) return
        setSwitched(r)
        setSourceDir(r.sourceDir)
        if (r.createdDefault) toast(`已生成《${r.gameName}》初始默认备份`, 'success')
      })
      .then(() => refresh())
      .catch((e) => toast(String(e), 'error'))
    return () => {
      cancelled = true
    }
  }, [gameKey, refresh])

  // 定时刷新(对应 QTimer, 间隔取自 config.app.table_refresh)
  useEffect(() => {
    if (!config) return
    const id = setInterval(() => refresh(), config.app.table_refresh)
    return () => clearInterval(id)
  }, [config, refresh])

  const games = config?.games ?? {}

  const handlePickSource = async (): Promise<void> => {
    const p = await window.api.pickSource()
    if (p) {
      setSourceDir(p)
      toast('源目录已更新(本次会话生效)', 'success')
    }
  }

  const handleCreate = async (): Promise<void> => {
    if (busy) return
    setBusy(true)
    try {
      await window.api.createArchive(gameKey, name, sourceDir)
      setName('')
      toast('存档成功', 'success')
      await refresh()
    } catch (e) {
      toast(String(e), 'error')
    } finally {
      setBusy(false)
    }
  }

  const handleRestore = async (a: ArchiveInfo): Promise<void> => {
    const ok = await confirm('确认回档', `将回档至《${a.name}》, 当前源目录文件会被覆盖, 是否继续?`)
    if (!ok) return
    try {
      await window.api.restoreArchive(gameKey, a.path, sourceDir)
      toast(`回档《${a.name}》成功`, 'success')
      await refresh()
    } catch (e) {
      toast(String(e), 'error')
    }
  }

  const handleDelete = async (a: ArchiveInfo): Promise<void> => {
    const isDefault = a.fileName.endsWith('默认备份.zip')
    const ok = await confirm(
      isDefault ? '删除默认存档' : '删除存档',
      isDefault
        ? `《${a.name}》是默认存档, 删除后将无法恢复初始存档, 确定?`
        : `确认删除《${a.name}》?`
    )
    if (!ok) return
    try {
      await window.api.deleteArchive(gameKey, a.path)
      toast('删除成功', 'success')
      await refresh()
    } catch (e) {
      toast(String(e), 'error')
    }
  }

  const handleRestoreLatest = async (): Promise<void> => {
    if (archives.length === 0) {
      toast('暂无存档', 'info')
      return
    }
    await handleRestore(archives[0])
  }

  const handleRestoreInit = async (): Promise<void> => {
    if (!switched) return
    const initName = `${switched.gameName}默认备份`
    const init = archives.find((a) => a.name === initName)
    if (!init) {
      toast('未找到初始默认存档', 'error')
      return
    }
    await handleRestore(init)
  }

  const handleOpen = async (path: string): Promise<void> => {
    try {
      await window.api.openPath(path)
    } catch (e) {
      toast(String(e), 'error')
    }
  }

  if (!config) return <div className="loading">加载中…</div>

  return (
    <div className="app">
      <TitleBar />
      <header className="app-header">
        <div className="current-game">{switched?.gameName ?? '—'}</div>
        <GameSelector games={games} value={gameKey} onChange={setGameKey} />
      </header>

      <main className="app-main">
        <SourceBar
          sourceDir={sourceDir}
          onPick={handlePickSource}
          onOpen={() => handleOpen(sourceDir)}
        />

        <ArchiveForm name={name} setName={setName} onCreate={handleCreate} busy={busy} />

        <ActionBar
          onRestoreLatest={handleRestoreLatest}
          onRestoreInit={handleRestoreInit}
          onRefresh={refresh}
        />

        <LatestArchive name={archives[0]?.name ?? ''} />

        <ArchiveTable
          archives={archives}
          onOpen={(a) => handleOpen(a.path)}
          onRestore={handleRestore}
          onDelete={handleDelete}
        />
      </main>

      <ConfirmDialog ref={confirmRef} />
      <Toast ref={toastRef} />
    </div>
  )
}
