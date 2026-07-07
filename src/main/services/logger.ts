import log from 'electron-log'

// 文件日志写到 userData/logs/main.log, 同时输出控制台
log.transports.file.level = 'info'
log.transports.console.level = 'info'
log.transports.file.format = '{y}-{m}-{d} {h}:{i}:{s}.{ms} [{level}] {text}'

export default log
