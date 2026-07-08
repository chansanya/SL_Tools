import { ipcMain, dialog, shell, BrowserWindow } from 'electron'
import { getConfig } from './services/config'
import { resolveBackPath, resolveSourcePath } from './services/env'
import {
  listArchives,
  createBackup,
  ensureDefaultBackup,
  restoreBackup,
  deleteBackup
} from './services/backup'
import type { ArchiveInfo, GameConfig } from '../shared/types'
import log from './services/logger'

/** 取游戏配置 + 展开后的 source / 原始 back */
function gameOf(key: string): { cfg: GameConfig; source: string; back: string } {
  const games = getConfig().games
  const cfg = games[key]
  if (!cfg) throw new Error(`未知游戏标识: ${key}`)
  return { cfg, source: resolveSourcePath(cfg.source), back: cfg.back ?? './back' }
}

/** 统一异常处理: 记录日志后抛出, 由前端 invoke().catch 接管弹窗 */
async function wrap<T>(fn: () => T | Promise<T>): Promise<T> {
  try {
    return await fn()
  } catch (e) {
    log.error(String(e))
    throw e instanceof Error ? e : new Error(String(e))
  }
}

export function registerIpc(): void {
  ipcMain.handle('config:get', () => wrap(() => getConfig()))

  ipcMain.handle('game:switch', (_e, key: string) =>
    wrap(() => {
      const { cfg, source, back } = gameOf(key)
      const r = ensureDefaultBackup(source, back, key, cfg.name)
      return {
        gameKey: key,
        gameName: cfg.name,
        sourceDir: source,
        backDir: resolveBackPath(back),
        createdDefault: r.created
      }
    })
  )

  ipcMain.handle('archive:list', (_e, key: string) =>
    wrap(() => {
      const { back } = gameOf(key)
      return listArchives(back, key) as ArchiveInfo[]
    })
  )

  ipcMain.handle('archive:create', (_e, key: string, name?: string, sourceOverride?: string) =>
    wrap(() => {
      const g = gameOf(key)
      return createBackup(sourceOverride ?? g.source, g.back, key, name)
    })
  )

  ipcMain.handle('archive:restore', (_e, key: string, zipPath: string, sourceOverride?: string) =>
    wrap(() => {
      const g = gameOf(key)
      restoreBackup(zipPath, sourceOverride ?? g.source)
      return true
    })
  )

  ipcMain.handle('archive:delete', (_e, _key: string, zipPath: string) =>
    wrap(() => {
      deleteBackup(zipPath)
      return true
    })
  )

  ipcMain.handle('dialog:pickSource', (e) =>
    wrap(async () => {
      const win = BrowserWindow.fromWebContents(e.sender) ?? undefined
      const r = await dialog.showOpenDialog(win!, { properties: ['openDirectory'] })
      if (r.canceled || r.filePaths.length === 0) return null
      return r.filePaths[0].replace(/\\/g, '/')
    })
  )

  ipcMain.handle('shell:openPath', (_e, p: string) => wrap(() => shell.openPath(p)))

  // 窗口控制(frameless 自定义标题栏), 单向 send 即可
  ipcMain.on('window:minimize', (e) => BrowserWindow.fromWebContents(e.sender)?.minimize())
  ipcMain.on('window:maximize-toggle', (e) => {
    const w = BrowserWindow.fromWebContents(e.sender)
    if (!w) return
    if (w.isMaximized()) w.unmaximize()
    else w.maximize()
  })
  ipcMain.on('window:close', (e) => BrowserWindow.fromWebContents(e.sender)?.close())
}
