import { contextBridge, ipcRenderer } from 'electron'

/** 暴露给渲染进程的安全 API 白名单, 不泄漏 Node 能力 */
const api = {
  getConfig: () => ipcRenderer.invoke('config:get'),
  switchGame: (key: string) => ipcRenderer.invoke('game:switch', key),
  listArchives: (key: string) => ipcRenderer.invoke('archive:list', key),
  createArchive: (key: string, name?: string, source?: string) =>
    ipcRenderer.invoke('archive:create', key, name, source),
  restoreArchive: (key: string, zipPath: string, source?: string) =>
    ipcRenderer.invoke('archive:restore', key, zipPath, source),
  deleteArchive: (key: string, zipPath: string) =>
    ipcRenderer.invoke('archive:delete', key, zipPath),
  pickSource: () => ipcRenderer.invoke('dialog:pickSource'),
  openPath: (p: string) => ipcRenderer.invoke('shell:openPath', p),
  minimize: () => ipcRenderer.send('window:minimize'),
  toggleMaximize: () => ipcRenderer.send('window:maximize-toggle'),
  closeWindow: () => ipcRenderer.send('window:close')
}

contextBridge.exposeInMainWorld('api', api)

export type SlApi = typeof api
