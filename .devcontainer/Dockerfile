FROM mcr.microsoft.com/devcontainers/python:1-3.11-bookworm

USER root

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
       chromium \
       xvfb \
       x11vnc \
       novnc \
       websockify \
       ca-certificates \
       dbus-x11 \
    && rm -rf /var/lib/apt/lists/*

USER vscode
