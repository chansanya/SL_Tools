import AdmZip from 'adm-zip'
import fs from 'fs'
import path from 'path'
import log from './logger'
import { resolveBackPath, resolveSourcePath } from './env'
import type { ArchiveInfo } from '../../shared/types'

const DEFAULT_SUFFIX = '默认备份'

function backupDirOf(back: string, gameKey: string): string {
  return path.join(resolveBackPath(back), gameKey)
}

/** 扫描某游戏的备份目录, 返回按时间倒序的存档列表 (对应 refresh_table) */
export function listArchives(back: string, gameKey: string): ArchiveInfo[] {
  const dir = backupDirOf(back, gameKey)
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true })
    return []
  }
  return fs
    .readdirSync(dir)
    .filter((f) => f.toLowerCase().endsWith('.zip'))
    .map((f) => {
      const full = path.join(dir, f)
      const stat = fs.statSync(full)
      return {
        fileName: f,
        name: f.replace(/\.zip$/i, ''),
        path: full,
        ctime: stat.ctimeMs
      }
    })
    .sort((a, b) => b.ctime - a.ctime)
}

/** 压源目录为 zip; archiveName 为空则用时间戳 (对应 start_backup) */
export function createBackup(
  source: string,
  back: string,
  gameKey: string,
  archiveName?: string
): { zipPath: string; name: string } {
  const src = resolveSourcePath(source)
  if (!src || !fs.existsSync(src)) {
    throw new Error(`源目录不存在: ${src}`)
  }
  const name = archiveName && archiveName.trim() ? archiveName.trim() : timestamp()
  const dir = backupDirOf(back, gameKey)
  fs.mkdirSync(dir, { recursive: true })
  const zipPath = path.join(dir, `${name}.zip`)

  const zip = new AdmZip()
  zip.addLocalFolder(src)
  zip.writeZip(zipPath)
  log.info(`存档完成: ${zipPath}`)
  return { zipPath, name }
}

/** 切换游戏时调用: 若「{游戏名}默认备份」不存在则生成 (对应 start_backup_at_startup) */
export function ensureDefaultBackup(
  source: string,
  back: string,
  gameKey: string,
  gameName: string
): { created: boolean; name: string } {
  const name = `${gameName}${DEFAULT_SUFFIX}`
  const zipPath = path.join(backupDirOf(back, gameKey), `${name}.zip`)
  if (fs.existsSync(zipPath)) {
    log.warn(`默认备份已存在, 跳过: ${zipPath}`)
    return { created: false, name }
  }
  createBackup(source, back, gameKey, name)
  return { created: true, name }
}

/** 解压覆盖到源目录 (对应 restore_backup; 保持原版「直接覆盖」语义) */
export function restoreBackup(zipPath: string, source: string): void {
  if (!fs.existsSync(zipPath)) {
    throw new Error(`存档文件不存在: ${zipPath}`)
  }
  const src = resolveSourcePath(source)
  fs.mkdirSync(src, { recursive: true })
  const zip = new AdmZip(zipPath)
  zip.extractAllTo(src, true)
  log.info(`回档完成: ${zipPath} -> ${src}`)
}

export function deleteBackup(zipPath: string): void {
  if (!fs.existsSync(zipPath)) {
    throw new Error(`存档文件不存在: ${zipPath}`)
  }
  fs.rmSync(zipPath, { force: true })
  log.info(`删除存档: ${zipPath}`)
}

/** 判断是否默认备份(前端据此弹二次确认) */
export function isDefaultBackupName(fileName: string): boolean {
  return fileName.endsWith(`${DEFAULT_SUFFIX}.zip`)
}

function timestamp(): string {
  const d = new Date()
  const p = (n: number): string => String(n).padStart(2, '0')
  return `${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}${p(d.getHours())}${p(
    d.getMinutes()
  )}${p(d.getSeconds())}`
}
