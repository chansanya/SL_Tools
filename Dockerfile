# 在 Linux/WSL/macOS 上打 Windows 安装包的构建镜像。
# electron-builder 生成 nsis 安装包时, 要用 wine 跑 NSIS 编译器(32 位), 所以装 wine32+64。
#
# 下面基础镜像走 daocloud、apt 走清华源是国内加速;
# 海外或自建 registry 换回官方即可:  FROM node:20-bookworm-slim  并删掉换源那两行 sed。
FROM docker.m.daocloud.io/library/node:20-bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive WINEDEBUG=-all

RUN sed -i 's|deb.debian.org|mirrors.tuna.tsinghua.edu.cn|g; s|security.debian.org|mirrors.tuna.tsinghua.edu.cn|g' \
        /etc/apt/sources.list.d/debian.sources 2>/dev/null; \
    sed -i 's|deb.debian.org|mirrors.tuna.tsinghua.edu.cn|g; s|security.debian.org|mirrors.tuna.tsinghua.edu.cn|g' \
        /etc/apt/sources.list 2>/dev/null; \
    dpkg --add-architecture i386 && \
    apt-get update && \
    apt-get install -y --no-install-recommends wine wine32 wine64 ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# 内置镜像源(国内加速), docker run 不必再传 -e
ENV ELECTRON_MIRROR=https://npmmirror.com/mirrors/electron/
ENV ELECTRON_BUILDER_BINARIES_MIRROR=https://npmmirror.com/mirrors/electron-builder-binaries/

WORKDIR /project
