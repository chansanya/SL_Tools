# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

SL工具：单机游戏存档的存档/回档桌面应用。Electron + React + TypeScript 实现，深色游戏风 UI，目标平台 Windows。由原 Python + PyQt5 版本重写而来（旧代码在 git `master` 分支历史）。

核心机制：将游戏源存档目录用 adm-zip 压缩成 `.zip` 备份，解压覆盖实现回档。游戏列表、路径、刷新间隔全部由 `config.yaml` 驱动。

## 常用命令

```shell
npm install        # 安装依赖
npm run dev        # 开发模式(electron-vite, 热更新)
npm run build      # 构建主进程/preload/renderer → out/
npm run typecheck  # tsc 类型检查(node 端 + web 端)
npm run build:win  # 打 Windows nsis 安装包(需 Windows 环境, 产物在 dist/)
```

**注意**：Linux/macOS 打 Windows 包需要 wine；本仓库只在 Windows 上执行 `build:win`。无单元测试框架，改动靠 `npm run typecheck` + `npm run dev` 手动验证。

## 架构

四层结构，职责严格分离：

- **主进程** [src/main/](src/main/)：Node 环境，负责窗口、文件系统、压缩解压。
  - [index.ts](src/main/index.ts)：创建 `BrowserWindow`（**frameless 无边框**，自定义标题栏）、加载 renderer、注册 IPC。
  - [ipc.ts](src/main/ipc.ts)：**所有 `ipcMain.handle/on` 的唯一入口**，薄封装，转发到 services。
  - [services/config.ts](src/main/services/config.ts)：`config.yaml` 读写 + 首次启动自举默认配置（移植自 Python `check_file`）。
  - [services/env.ts](src/main/services/env.ts)：`%APPDATA%` 环境变量展开（自写 `expandEnvVars`，Node 无 `os.path.expandvars`）、相对 `back` 路径基于 exe 目录解析。
  - [services/backup.ts](src/main/services/backup.ts)：压缩/解压/删除/列表/默认备份自检，**核心业务逻辑**。
  - [services/logger.ts](src/main/services/logger.ts)：electron-log，写 `userData/logs/main.log`。
- **预加载** [src/preload/index.ts](src/preload/index.ts)：用 `contextBridge.exposeInMainWorld` 暴露白名单 `window.api`，不泄漏 Node 能力（`contextIsolation: true`，`nodeIntegration: false`，`sandbox: false`）。
- **渲染进程** [src/renderer/](src/renderer/)：React 18，纯 UI + 状态，通过 `window.api` 调主进程。
- **共享类型** [src/shared/types.ts](src/shared/types.ts)：**三端共享的纯类型契约**，关键是 `SlApi` 接口——它既是 preload 实现的约束，也是 renderer 的 `window.api` 类型来源。改 IPC 签名必须同步改这里。

## 核心数据流（理解这个就理解整个应用）

1. 启动 → `ensureConfig()` 确保 `userData/config.yaml` 存在 → 注册 IPC → 建窗口。
2. renderer `getConfig()` → 取 `games` → 默认选首个游戏。
3. 选游戏 → `switchGame(key)` → 主进程 `ensureDefaultBackup`（首次生成 `{游戏名}默认备份.zip` 作为「回档至初始」基准）→ 返回展开后的 `sourceDir`/`backDir`。
4. renderer 持有 `sourceDir`（可被「重新选择」覆盖，本次会话生效），存档/回档时透传给主进程。
5. 存档 → `createArchive(key, name, source)` → adm-zip `addLocalFolder` 压源目录为 `{back}/{key}/{name}.zip`，名空用时间戳。
6. 回档 → `restoreArchive(key, zipPath, source)` → adm-zip `extractAllTo(overwrite=true)`，**保持原版「直接覆盖」语义**（不先清空）。
7. 列表 → `listArchives(key)` 扫子目录、按 ctime 倒序；renderer `setInterval(app.table_refresh)` 周期刷新（对应原 PyQt QTimer）。

## IPC 协议

见 [src/shared/types.ts](src/shared/types.ts) 的 `SlApi`。要点：
- `config:get` / `game:switch` / `archive:list` / `archive:create` / `archive:restore` / `archive:delete` / `dialog:pickSource` / `shell:openPath` 用 `ipcMain.handle`（有返回）。
- `window:minimize` / `window:maximize-toggle` / `window:close` 用 `ipcMain.on`（单向，frameless 标题栏用）。
- 主进程 `wrap()` 统一捕获异常并 `log.error` 后抛出，renderer 端 `.catch` 弹 Toast。

## UI 与主题

深色游戏风，色板贴近黑神话悟空（橙红 `#d4622a`）/ 法环（暗金 `#c9a227`）。全部样式在 [src/renderer/src/styles/](src/renderer/src/styles/)：`theme.css`（CSS 变量）、`global.css`（按钮/输入/卡片/表格/标题栏/模态/Toast 工具类）。**不使用 UI 库或 Tailwind**——主题高度定制，纯 CSS 最轻最可控。改配色只动 `theme.css` 变量。

标题栏是 frameless 自绘组件 [components/TitleBar.tsx](src/renderer/src/components/TitleBar.tsx)，拖拽靠 `-webkit-app-region: drag`，按钮区 `no-drag`。

## 配置位置

- 配置文件：`app.getPath('userData')/config.yaml`（不是工作目录，打包后仍可写）。
- 备份目录：`back` 字段相对 **exe 所在目录**解析（开发期相对 electron 开发版 exe，意义不大；打包后与 exe 同级、用户可见）。
- 日志：`userData/logs/main.log`。

## 修改要点

- **新增游戏**：只改 `config.yaml`（及 [config.ts](src/main/services/config.ts) 的 `defaultConfig` 模板，保证首次生成的配置含该游戏），不动代码。
- **改 IPC**：必须同步 [shared/types.ts](src/shared/types.ts) 的 `SlApi` + [preload/index.ts](src/preload/index.ts) 实现 + [ipc.ts](src/main/ipc.ts) handler 三处。
- **回档语义**：当前是「覆盖不解空」，与原 Python 版一致；若要「干净回档」属增强，需先清空源目录再解压。
- **中文文件名压缩**：adm-zip 默认 UTF-8 文件名标志，Windows 资源管理器解压一般正常；若遇乱码需在 `createBackup` 处理编码。
- **依赖卫生**：`package.json` 中 `@electron-toolkit/utils`/`@electron-toolkit/preload` 为历史残留未用（主进程入口已改用原生 `app` API，不再依赖 toolkit），可清理。

## 已知环境限制（开发机）

本仓库在 WSL2 开发。验证 electron 时若 `require('electron').app` 为 `undefined`、`electron --version` 返回的是 Node 版本，是环境变量 `ELECTRON_RUN_AS_NODE=1` 导致 electron 退化为纯 Node——`env -u ELECTRON_RUN_AS_NODE npx electron .` 即可。此变量仅本机有，Windows 用户不受影响。
