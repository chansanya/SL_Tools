# SL工具

单机游戏存档的「存档（Save）/ 回档（Load）」桌面工具。把游戏存档目录压缩成 ZIP 实现备份，解压覆盖实现回档。内置支持艾尔登法环、黑神话悟空，**新增游戏只需改一处配置**。

基于 Electron + React + TypeScript 重写，Ant Design 浅色 UI，支持 Windows 一键安装。

## 功能

- 多游戏切换（配置驱动）
- 一键存档（自动以时间戳命名，或自定义存档名）
- 回档至最新 / 回档至初始（自动生成的默认备份）
- 存档列表：打开目录、回档、删除（删默认备份有二次确认）
- 重新选择源目录（本次会话生效）
- 定时自动刷新存档列表

## 技术栈

- **Electron 33** + **electron-vite** + **electron-builder**
- **React 18** + **TypeScript 5** + **Ant Design 5**（UI 组件库）
- **adm-zip**（压缩/解压）· **js-yaml**（配置）· **electron-log**（日志）

## 开发

```shell
npm install        # 安装依赖
npm run dev        # 启动开发(热更新)
```

## 构建

```shell
npm run build      # 编译主进程/preload/renderer 到 out/
npm run typecheck  # 类型检查
```

## 打包 Windows 可执行文件

一次打包产出**两个版本**（都在 `dist/`）：

- **`SL工具 Setup <version>.exe`** — NSIS 安装版：可选安装路径、建桌面/开始菜单快捷方式；配置存 `%APPDATA%\SL工具\`。
- **`SL工具-绿色版-<version>.exe`** — 免安装便携版：单文件，**双击即用**，配置和备份随 exe 携带（exe 同级生成 `data/` 和 `back/`），拷到 U 盘换机器也能跑。

### 方式一：Windows 本机（最简单）

```shell
npm run build:win  # 产出 dist/SL工具 Setup <version>.exe
```

### 方式二：Linux / WSL / macOS 用 Docker

非 Windows 环境打 Windows nsis 包需要 wine。本项目提供 Dockerfile（含 wine32+64），一键脚本：

```shell
bash scripts/build-win.sh
```

脚本自动完成：构建含 wine 的镜像 → 容器内 `npm ci && npm run build:win` → 产物落到 `dist/`。

- 容器内用 npmmirror 加速 electron 和 nsis 资源下载
- 用独立卷 `sl-node-modules` 装依赖，**不污染本机 node_modules**
- 镜像内 apt 换清华源加速 wine 安装；海外构建可改 Dockerfile 换回官方源

> 若 Docker 拉基础镜像失败，把 Dockerfile 的 `FROM` 改成你能访问的 registry 镜像。

**应用图标**：在 `build/` 放置 `icon.ico`（或 256×256 以上的 `icon.png`），然后取消 `electron-builder.yml` 中 `win.icon` 的注释。

## 配置

首次启动会在用户目录生成默认配置：

- Windows: `%APPDATA%/SL工具/config.yaml`
- Linux: `~/.config/SL工具/config.yaml`

配置示例与字段：

```yaml
app:
  table_refresh: 30000   # 存档列表自动刷新间隔(ms)
windows:
  w: 760                 # 窗口宽
  h: 540                 # 窗口高
games:
  EldenRing:
    name: '艾尔登法环'
    source: '%APPDATA%/EldenRing/'   # 源存档目录, 支持 %APPDATA% 等环境变量
    back: './back'                   # 备份根目录, 可省略(默认 ./back), 相对 exe 所在目录
    is_default: true
  wu-kong:
    name: '黑神话悟空'
    source: '%APPDATA%/wu-kong/'
    # back 省略, 默认 ./back
    is_default: false
```

### 新增游戏

在 `config.yaml` 的 `games` 下追加一项即可，无需改动代码：

```yaml
  NewGame:
    name: '新游戏'
    source: '%APPDATA%/NewGame/'
    # back 可省略, 默认 ./back
```

`source` 支持 `%APPDATA%`、`%USERPROFILE%`、`%LOCALAPPDATA%` 等 Windows 环境变量。
`back` 省略时默认 `./back`（相对 exe 所在目录）。

## 目录结构

```
src/
├── main/              主进程: 窗口、IPC、文件操作服务
│   ├── index.ts
│   ├── ipc.ts
│   └── services/      config / env / backup / logger
├── preload/           预加载: contextBridge 安全暴露 window.api
├── renderer/          渲染进程: React UI
│   └── src/
│       ├── App.tsx
│       ├── components/
│       └── styles/    global.css(布局/标题栏)
└── shared/            三端共享类型契约(纯类型)
```

## 备份存放位置

每个游戏的存档按游戏标识分子目录隔离：

```
{back}/{游戏标识}/{存档名}.zip
```

例如 `./back/EldenRing/20260707120000.zip`、`./back/EldenRing/艾尔登法环默认备份.zip`。

## 从 Python 版迁移

本项目由原 Python + PyQt5 版本重写而来（见 git 历史 `master` 分支）。功能 1:1 还原，并修复了原版「重新选择源目录」未真正生效的问题。
