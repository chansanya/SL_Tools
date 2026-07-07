import { app } from 'electron'
import fs from 'fs'
import path from 'path'
import yaml from 'js-yaml'
import log from './logger'
import type { GameConfig, SLConfig } from '../../shared/types'

export type { GameConfig, SLConfig }

/** 默认配置, 首次启动写入 userData/config.yaml (移植自 Python 版 default_config) */
const defaultConfig: SLConfig = {
  app: { table_refresh: 30000 },
  windows: { w: 760, h: 540 },
  games: {
    EldenRing: {
      name: '艾尔登法环',
      source: '%APPDATA%/EldenRing/',
      back: './back',
      is_default: true
    },
    'wu-kong': {
      name: '黑神话悟空',
      source: '%APPDATA%/wu-kong/',
      back: './back',
      is_default: false
    }
  }
}

export function configPath(): string {
  return path.join(app.getPath('userData'), 'config.yaml')
}

/** 首次启动自举写入默认配置, 对应 Python check_file() */
export function ensureConfig(): void {
  const p = configPath()
  if (!fs.existsSync(p)) {
    fs.writeFileSync(p, yaml.dump(defaultConfig, { lineWidth: -1 }), 'utf-8')
    log.info(`配置不存在, 已写入默认配置: ${p}`)
  }
}

export function getConfig(): SLConfig {
  ensureConfig()
  const raw = fs.readFileSync(configPath(), 'utf-8')
  const cfg = yaml.load(raw) as SLConfig
  if (!cfg || !cfg.games) {
    throw new Error('配置为空或缺少 games 节, 请检查 config.yaml')
  }
  return cfg
}
