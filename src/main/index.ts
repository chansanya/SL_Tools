import { app, BrowserWindow, shell } from 'electron'
import path from 'path'
import { ensureConfig, getConfig } from './services/config'
import { registerIpc } from './ipc'
import log from './services/logger'

let mainWindow: BrowserWindow | null = null

function createWindow(): void {
  const win = getConfig().windows ?? { w: 760, h: 540 }

  mainWindow = new BrowserWindow({
    width: win.w ?? 760,
    height: win.h ?? 540,
    minWidth: 680,
    minHeight: 460,
    show: false,
    autoHideMenuBar: true,
    frame: false,
    title: 'SL工具',
    backgroundColor: '#f5f7fa',
    webPreferences: {
      preload: path.join(__dirname, '../preload/index.js'),
      sandbox: false,
      contextIsolation: true,
      nodeIntegration: false
    }
  })

  mainWindow.on('ready-to-show', () => mainWindow?.show())
  mainWindow.on('closed', () => {
    mainWindow = null
  })

  // 把 renderer 控制台/崩溃日志转到主进程 stdout, 便于诊断
  mainWindow.webContents.on('console-message', (_e, level, message) =>
    log.info(`[renderer:${level}] ${message}`)
  )
  mainWindow.webContents.on('render-process-gone', (_e, d) =>
    log.error(`[renderer-gone] reason=${d.reason} exitCode=${d.exitCode}`)
  )

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url)
    return { action: 'deny' }
  })

  // dev: electron-vite 注入 ELECTRON_RENDERER_URL; 生产: 加载打包后的 index.html
  const devUrl = process.env['ELECTRON_RENDERER_URL']
  if (devUrl) {
    mainWindow.loadURL(devUrl)
  } else {
    mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'))
  }
}

app.whenReady().then(() => {
  app.setAppUserModelId('com.chansanya.sltools')
  ensureConfig()
  registerIpc()
  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})
