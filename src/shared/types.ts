/** 三端(main / preload / renderer)共享的类型契约。纯类型, 无运行时代码, 无 Node 依赖。 */

export interface GameConfig {
  name: string
  source: string
  /** 备份根目录, 相对 exe 所在目录; 省略则默认 './back' */
  back?: string
  is_default?: boolean
}

export interface SLConfig {
  app: { table_refresh: number }
  windows: { w: number; h: number }
  games: Record<string, GameConfig>
}

export interface ArchiveInfo {
  /** 存档名(不含 .zip) */
  name: string
  /** 文件名(含 .zip) */
  fileName: string
  /** 绝对路径 */
  path: string
  /** 创建时间戳(ms) */
  ctime: number
}

export interface SwitchGameResult {
  gameKey: string
  gameName: string
  sourceDir: string
  backDir: string
  createdDefault: boolean
}

export interface CreateArchiveResult {
  zipPath: string
  name: string
}

/** IPC 契约: preload 实现须满足, renderer 据此获得 window.api 类型提示 */
export interface SlApi {
  getConfig: () => Promise<SLConfig>
  switchGame: (key: string) => Promise<SwitchGameResult>
  listArchives: (key: string) => Promise<ArchiveInfo[]>
  createArchive: (key: string, name?: string, source?: string) => Promise<CreateArchiveResult>
  restoreArchive: (key: string, zipPath: string, source?: string) => Promise<boolean>
  deleteArchive: (key: string, zipPath: string) => Promise<boolean>
  pickSource: () => Promise<string | null>
  openPath: (p: string) => Promise<string>
  minimize: () => void
  toggleMaximize: () => void
  closeWindow: () => void
}
