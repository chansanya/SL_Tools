import path from 'path'
import { app } from 'electron'

/**
 * 展开 %APPDATA% / %USERPROFILE% 等环境变量, 对应 Python os.path.expandvars。
 * 大小写不敏感; 未命中则原样保留占位。
 */
export function expandEnvVars(input: string): string {
  if (!input) return ''
  return input.replace(/%([^%]+)%/g, (_, name: string) => {
    const upper = name.toUpperCase()
    return process.env[upper] ?? process.env[name] ?? ''
  })
}

/** 展开环境变量并统一为正斜杠路径 */
export function normalizePath(input: string): string {
  return expandEnvVars(input).replace(/\\/g, '/')
}

/**
 * 备份根目录解析:
 * - 绝对路径: 原样
 * - 相对路径: 以「exe 所在目录」为基准(贴近 Python 版运行时 cwd 行为, 打包后 back/ 与 exe 同级、用户可见)
 */
export function resolveBackPath(back: string): string {
  const p = normalizePath(back)
  if (path.isAbsolute(p)) return p
  const exeDir = path.dirname(app.getPath('exe'))
  return path.join(exeDir, p)
}

export function resolveSourcePath(source: string): string {
  return normalizePath(source)
}
