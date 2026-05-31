# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

创作者多平台内容适配与发布助手（Creator Content Publisher）。用户输入一份原始内容，系统自动生成适合公众号、知乎、B站、小红书、抖音、快手等平台的草稿，并提供预览编辑、模拟发布、浏览器辅助发布、公众号草稿发布和发布历史管理能力。

- **前端**: Vue 3 + Vite + Element Plus + Pinia + Vue Router
- **后端**: Flask + SQLite
- **设计系统**: Warm Teal 暖色调主题，Plus Jakarta Sans 字体，Element Plus Icons

## 架构

```text
frontend/                   Vue 3 + Vite 前端
  src/api/                  API 请求封装（axios）
  src/components/           通用组件（AppLayout）
  src/router/               前端路由
  src/stores/               Pinia 状态管理（app, content）
  src/styles/               全局样式（main.scss — 设计 Token 系统）
  src/utils/                工具函数（platformName）
  src/views/                页面视图（7个页面）

backend/                    Flask + SQLite 后端
  adapters/                 平台内容适配器（6个平台）
  publishers/               平台发布器（浏览器自动化 + API）
  repositories/             SQLite 数据访问层
  routes/                   HTTP API 路由（Blueprints）
  services/                 业务编排服务
  models/                   领域模型（预留，当前空置）
  schemas/                  请求/响应模式（预留，当前空置）
  config.py                 配置与环境变量加载
  db.py                     数据库连接
  init_db.py                数据库初始化与迁移
  app.py                    Flask 入口
```

## 后端分层

| 层级 | 目录 | 职责 |
|------|------|------|
| routes | `backend/routes/` | 暴露 HTTP API，参数校验，返回 JSON |
| services | `backend/services/` | 编排内容、草稿、发布任务等业务流程 |
| repositories | `backend/repositories/` | SQLite CRUD 操作（content_repository, platform_draft_repository, publish_task_repository） |
| adapters | `backend/adapters/` | 将统一内容转换为各平台草稿（6个平台适配器） |
| publishers | `backend/publishers/` | 真实发布、浏览器辅助发布、公众号 API 发布 |

## 平台支持一览

| 平台 | platform_key | 适配器 | 发布方式 |
|------|-------------|--------|---------|
| 公众号 | wechat_official | ✅ | 微信 API 草稿发布 |
| 知乎 | zhihu | ✅ | 浏览器发布助手 |
| B站 | bilibili | ✅ | 浏览器辅助发布 |
| 小红书 | xiaohongshu | ✅ | 浏览器发布助手 |
| 抖音 | douyin | ✅ | 浏览器辅助发布 |
| 快手 | kuaishou | ✅ | 浏览器发布助手 |

## 常用命令

### 后端

```bash
cd backend && pip install -r requirements.txt   # 安装依赖
py -m backend.app                                # 启动开发服务器 (端口 5409)
py -m compileall backend                         # 语法检查
```

### 前端

```bash
cd frontend && npm install                       # 安装依赖
cd frontend && npm run dev                       # 启动开发服务器 (端口 5173)
cd frontend && npm run build                     # 构建生产版本
```

## 开发注意事项

- 后端 `app.py` 仅负责创建 Flask 应用、注册 Blueprint、初始化数据库，业务逻辑在 services 层
- 新增平台需在 `adapters/registry.py` 注册适配器，在 `publishers/` 新增发布器
- 浏览器发布器的统一模式：获取草稿 → 创建任务 → 打开页面 → 填充内容 → 返回 manual_pending 等待人工确认
- 数据目录 `backend/data/` 包含运行时数据（数据库、cookies、视频、日志），由 `.gitignore` 排除
- 前端样式 Token 集中在 `frontend/src/styles/main.scss` 的 `:root` 中定义，不硬编码颜色值
- 前端页面使用 `<AppLayout>` 包裹，侧栏导航由 AppLayout 统一管理
- Git commit message 使用中文
