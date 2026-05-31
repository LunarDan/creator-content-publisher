# 项目架构文档 / Creator Content Publisher

## 1. 项目定位

本项目是一个面向创作者的多平台内容适配与发布助手。用户只需要输入一份原始内容，系统就能生成公众号、知乎、B站、小红书、抖音、快手等平台的适配草稿，并支持预览、模拟发布、浏览器辅助发布和发布历史管理。

当前版本已从 Web-first MVP 演进为功能完整的多平台发布工具：支持 6 个平台的内容适配、5 个平台的浏览器辅助真实发布、公众号 API 草稿发布，以及模拟发布全流程。

---

## 2. 总体架构

系统采用前后端分离架构：

```text
Vue 前端 (Vite, port 5173)
  ↓ HTTP / JSON (开发环境通过 Vite proxy)
Flask 后端 (port 5409)
  ↓ SQLite / 适配器 / 发布器
本地数据与平台自动化
```

核心链路：

```text
用户输入内容
  ↓
后端保存统一内容模型
  ↓
平台适配器生成各平台草稿
  ↓
前端展示预览与编辑
  ↓
用户选择发布方式：
  ├── 模拟发布 → 发布历史记录
  ├── 浏览器辅助发布 → Playwright 自动化填充 → 人工确认 → 记录
  └── 公众号 API 发布 → 微信接口创建草稿 → 记录
```

---

## 3. 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Vue Router + Pinia + Element Plus 2 |
| 样式 | SCSS + CSS Custom Properties（设计 Token 系统） |
| 图标 | @element-plus/icons-vue |
| 后端 | Python + Flask |
| 数据库 | SQLite |
| 浏览器自动化 | Playwright（B站、抖音、小红书、快手、知乎） |
| API 发布 | 公众号微信接口 |
| 桌面端 | 预留 Tauri 扩展位置 |

---

## 4. 目录结构

```text
creator-content-publisher/
├── backend/
│   ├── app.py                    Flask 入口
│   ├── config.py                 配置与环境变量
│   ├── db.py                     数据库连接
│   ├── init_db.py                数据库初始化与迁移
│   ├── adapters/                 平台内容适配器
│   │   ├── base_adapter.py       适配器基类
│   │   ├── registry.py           适配器注册中心
│   │   ├── wechat_official.py    公众号
│   │   ├── zhihu.py              知乎
│   │   ├── bilibili.py           B站
│   │   ├── xiaohongshu.py        小红书
│   │   ├── douyin.py             抖音
│   │   └── kuaishou.py           快手
│   ├── publishers/               平台发布器
│   │   ├── registry.py           发布器注册
│   │   ├── wechat_official.py    公众号 API 发布
│   │   ├── zhihu_browser.py      知乎浏览器发布
│   │   ├── bilibili_browser.py   B站浏览器发布
│   │   ├── douyin_browser.py     抖音浏览器发布
│   │   ├── xiaohongshu_browser.py 小红书浏览器发布
│   │   └── kuaishou_browser.py   快手浏览器发布
│   ├── repositories/             SQLite 数据访问层
│   │   ├── content_repository.py
│   │   ├── platform_draft_repository.py
│   │   └── publish_task_repository.py
│   ├── routes/                   HTTP API 路由
│   │   ├── health.py             健康检查
│   │   ├── platforms.py          平台列表
│   │   ├── contents.py           内容 CRUD
│   │   └── publish.py            发布接口
│   ├── services/                 业务编排
│   │   └── content_service.py    核心服务
│   ├── models/                   领域模型（预留，当前空置）
│   └── schemas/                  请求/响应模式（预留，当前空置）
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── App.vue               根组件
│       ├── main.js               入口
│       ├── api/                  API 请求封装
│       │   ├── http.js           axios 实例
│       │   ├── content.js        内容接口
│       │   ├── platform.js       平台接口
│       │   └── publish.js        发布接口
│       ├── components/
│       │   └── AppLayout.vue     全局布局（侧栏 + 内容区）
│       ├── router/
│       │   └── index.js          路由配置
│       ├── stores/
│       │   ├── app.js            应用状态
│       │   └── content.js        内容状态
│       ├── styles/
│       │   └── main.scss         全局样式与设计 Token
│       ├── utils/
│       │   └── platform.js       平台名称映射
│       └── views/
│           ├── Dashboard.vue     仪表盘
│           ├── ContentEditor.vue 内容创作
│           ├── AdaptationCenter.vue 平台适配
│           ├── PreviewCenter.vue 预览中心
│           ├── PublishCenter.vue 发布中心
│           ├── PublishHistory.vue 发布历史
│           └── Settings.vue      系统设置
│
├── docs/
│   ├── api.md                    API 文档
│   └── architecture.md           架构文档（本文件）
│
├── .env.example                  环境变量模板
├── .gitignore
├── README.md
├── CLAUDE.md
└── package.json
```

---

## 5. 分层设计

### 5.1 前端层

前端负责用户交互和状态展示，主要页面：

- **Dashboard**：项目概览，统计卡片 + 最近内容列表
- **ContentEditor**：内容输入与生成平台草稿
- **AdaptationCenter**：平台草稿查看
- **PreviewCenter**：左右分栏预览与编辑
- **PublishCenter**：模拟发布 + 浏览器发布入口
- **PublishHistory**：发布任务历史与状态追踪
- **Settings**：平台配置说明

前端职责：
- 表单输入与校验
- 页面路由切换
- 调用后端 API
- 展示平台草稿和发布结果
- 管理页面级状态（Pinia）

设计原则：
- 设计 Token 集中在 `main.scss` 的 `:root` 中
- API 请求统一放在 `src/api/`
- 跨页面状态统一放在 `src/stores/`
- 页面使用 `<AppLayout>` 包裹，侧栏统一管理

### 5.2 后端层

后端负责业务逻辑、数据存储和平台适配。

分层：

```text
routes       HTTP 接口层 → 参数校验、返回 JSON
services     业务编排层 → 组织内容保存、适配、发布等流程
repositories 数据访问层 → SQLite CRUD
adapters     平台适配层 → 统一内容 → 平台草稿
publishers   发布执行层 → 浏览器自动化 / API 调用
```

入口为 `backend/app.py`，它只负责创建 Flask 应用、注册路由 Blueprint、初始化数据库。

---

## 6. 数据模型设计

### 6.1 Content

统一内容模型，用于保存用户输入的原始内容。

字段：`id`、`title`、`summary`、`body`、`cover_image`、`video_path`、`content_type`、`tags`、`created_at`、`updated_at`

### 6.2 PlatformDraft

平台草稿是内容适配后的结果。

字段：`id`、`content_id`、`platform`、`title`、`summary`、`body`、`tags`、`cover_image`、`extra_config`、`validation_warnings`、`created_at`、`updated_at`

### 6.3 PublishTask

发布任务记录一次模拟发布或真实发布。

字段：`id`、`content_id`、`platform_draft_id`、`platform`、`account_id`、`mode`、`status`、`title`、`error_message`、`publish_url`、`external_id`、`response_payload`、`created_at`、`started_at`、`finished_at`

---

## 7. 平台适配层设计

平台适配器负责把统一内容转换为不同平台风格的草稿。

### 7.1 适配器职责

- 调整标题长度和风格
- 调整正文结构和语气
- 生成平台推荐标签
- 提示平台限制和格式问题
- 输出平台草稿对象

### 7.2 适配器接口

```python
def transform(content) -> platform_draft
```

### 7.3 设计原则

- 平台差异放在适配器里，不放在页面里
- 新增平台时只增加适配器，不修改核心业务流程
- 适配器优先返回可预览、可编辑的数据结构

---

## 8. 发布层设计

### 8.1 发布模式

| 模式 | 说明 | 适用平台 |
|------|------|---------|
| `simulate` | 模拟发布，立即标记完成 | 所有平台 |
| `browser` | Playwright 浏览器自动化填充，人工确认发布 | 知乎、B站、抖音、小红书、快手 |
| `wechat_draft` | 微信公众号 API 创建草稿 | 公众号 |

### 8.2 浏览器发布器通用流程

```text
获取草稿 → 创建发布任务(状态: running)
  → 打开平台创作页
  → 上传视频/图片
  → 填充标题、正文、标签等字段
  → 返回 manual_pending，等待用户人工确认最终发布
  → 用户通过对话框确认完成 → 状态标记为 success
```

---

## 9. 前端数据流

### 9.1 内容创建流程

```text
ContentEditor
  ↓ 调用 contentApi.create
后端保存 Content
  ↓ 返回 content_id
  ↓ 调用 contentApi.adapt
  ↓ 生成 PlatformDraft
  ↓ 跳转 AdaptationCenter
```

### 9.2 预览流程

```text
AdaptationCenter / PreviewCenter
  ↓ 获取 platform drafts
  ↓ 渲染预览 + 编辑修改
  ↓ contentApi.updateDraft 保存
```

### 9.3 发布流程

```text
PublishCenter
  ↓ 选择平台草稿
  ├── 模拟发布 → publishApi.simulate / simulateBatch
  └── 真实发布 → 对应平台 browser/wechat API
  ↓ 发布历史记录
```

---

## 10. API 分层约定

所有接口统一采用：

```text
/api/...
```

返回格式统一为：

```json
{ "code": 200, "msg": "success", "data": {} }
```

完整接口文档见 `docs/api.md`。

---

## 11. 扩展更多平台的方式

### 11.1 扩展适配器

在 `backend/adapters/` 新增平台适配器：

- 继承 `BaseAdapter`
- 定义 `platform_key`、`platform_name`、`description`
- 实现 `transform(content)` 方法
- 在 `backend/adapters/registry.py` 中注册

### 11.2 扩展发布器

在 `backend/publishers/` 新增发布器：

- 浏览器辅助发布：继承 Playwright 模式，实现 `publish(draft, auto_publish)` 方法
- API 发布：实现平台 API 调用逻辑
- 在 `backend/services/content_service.py` 中增加对应方法
- 在 `backend/routes/publish.py` 中增加路由
- 在 `frontend/src/api/publish.js` 中增加 API 封装
- 在发布中心增加对应按钮

### 11.3 前端同步扩展

前端通过 `/api/platforms` 拉取平台配置，发布按钮按平台 key 条件渲染。

---

## 12. 运行时数据

```text
backend/data/
  ├── app.db            SQLite 数据库
  └── browser/          浏览器登录态
      ├── zhihu/
      ├── xiaohongshu/
      ├── douyin/
      ├── bilibili/
      └── kuaishou/
```

运行时数据由 `.gitignore` 排除，不提交到 Git。

---

## 13. 当前版本边界

当前版本已实现：

- ✅ 内容创作、编辑、删除
- ✅ 6 个平台内容适配
- ✅ 平台草稿预览与编辑
- ✅ 模拟发布（单个 + 批量）
- ✅ 公众号 API 草稿发布
- ✅ 知乎浏览器发布助手
- ✅ B站浏览器辅助发布
- ✅ 小红书浏览器发布助手
- ✅ 抖音浏览器辅助发布
- ✅ 快手浏览器发布助手
- ✅ 发布历史管理与人工确认
- ✅ 完整的设计 Token 系统

当前版本暂不包含：

- AI 内容改写
- 多用户权限系统
- Tauri 桌面端打包
- 账号管理系统
- 发布任务重试机制

---

## 14. 总结

本项目采用"统一内容模型 + 平台适配器 + 平台发布器"的架构方式，把创作者的一份内容转换成多个平台可用的发布版本。前端负责输入、展示和预览，后端负责存储、适配和发布任务。通过分层设计，项目已从 Web MVP 演进为功能完整的多平台发布工具，并支持后续扩展更多平台。
