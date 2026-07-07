#!/usr/bin/env bash
# 在 Linux / WSL / macOS 上用 Docker 打 Windows 安装包(无需本机装 wine)
# 产物: dist/SL工具 Setup <version>.exe
set -euo pipefail

# 切到项目根(本脚本位于 scripts/)
cd "$(dirname "$0")/.."

IMAGE="sl-wine-builder"

if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
  echo "==> [1/2] 构建 Docker 镜像 $IMAGE (node20 + wine32/64, 仅首次)"
  docker build -t "$IMAGE" .
else
  echo "==> [1/2] 镜像 $IMAGE 已存在, 跳过构建 (Dockerfile 改了要重建就先 docker rmi $IMAGE)"
fi

echo "==> [2/2] 容器内执行 npm ci + build:win ..."
docker run --rm \
  -e ELECTRON_MIRROR=https://npmmirror.com/mirrors/electron/ \
  -e ELECTRON_BUILDER_BINARIES_MIRROR=https://npmmirror.com/mirrors/electron-builder-binaries/ \
  -v "$(pwd):/project" \
  -v sl-node-modules:/project/node_modules \
  -w /project \
  "$IMAGE" \
  bash -c "npm ci && npm run build:win"

echo ""
echo "==> 完成, 安装包:"
ls -lh dist/*.exe 2>/dev/null || echo "  (没找到 exe, 请检查上面的错误日志)"
