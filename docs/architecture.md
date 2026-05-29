# 项目架构文档 / Creator Content Publisher

## 1. 项目定位

本项目是一个面向创作者的多平台内容适配与发布助手。用户只需要输入一份原始内容，系统就能生成公众号、知乎、B站、小红书等平台的适配草稿，并支持预览、模拟发布和后续真实发布扩展。

当前版本是 **Web-first MVP**：先完成内容输入、平台适配、草稿预览、模拟发布和发布历史，再逐步接入真实平台发布与桌面端能力。

---

## 2. 总体架构

系统采用前后端分离架构：

```text
Vue 前端
  ↓ HTTP / JSON
Flask 后端
  ↓ SQLite / 适配器 / 发布任务
本地数据与平台适配逻辑
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
用户执行模拟发布
  ↓
后端记录发布任务与历史
```

---

## 3. 技术栈

| 层级 | 技术 |
| --- | --- |
| 前端 | Vue 3 + Vite + Vue Router + Pinia + Element Plus |
| 后端 | Python + Flask |
| 数据库 | SQLite |
| 发布模式 | 先模拟发布，后真实发布 |
| 桌面端 | 预留 Tauri 扩展位置 |

---

## 4. 目录结构

```text
creator-content-publisher/
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── db.py
│   ├── init_db.py
│   ├── adapters/
│   ├── repositories/
│   ├── routes/
│   ├── services/
│   ├── models/
│   └── schemas/
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── api/
│       ├── components/
│       ├── router/
│       ├── stores/
│       ├── styles/
│       └── views/
│
├── docs/
│   ├── api.md
│   └── architecture.md
│
├── .gitignore
├── README.md
├── CLAUDE.md
└── package.json
```

---

## 5. 分层设计

### 5.1 前端层

前端负责用户交互和状态展示，主要页面包括：

- `Dashboard`：项目概览
- `ContentEditor`：内容输入与保存
- `AdaptationCenter`：平台草稿查看与适配结果展示
- `PreviewCenter`：各平台预览
- `PublishCenter`：模拟发布与后续真实发布入口
- `PublishHistory`：发布任务历史
- `Settings`：系统设置

前端职责：

- 表单输入与校验
- 页面路由切换
- 调用后端 API
- 展示平台草稿和发布结果
- 管理页面级状态

建议遵循的原则：

- 页面只负责展示和交互
- API 请求统一放在 `src/api/`
- 跨页面状态统一放在 `src/stores/`

---

### 5.2 后端层

后端负责业务逻辑、数据存储和平台适配。

后端分层：

```text
routes       HTTP 接口层
services     业务编排层
repositories 数据访问层
adapters     平台适配层
```

职责划分：

- `routes/`：接收请求、做基础参数校验、返回 JSON
- `services/`：组织内容保存、适配、发布等流程
- `repositories/`：只做 SQLite CRUD
- `adapters/`：把统一内容转换成各平台草稿

后端入口为 `backend/app.py`，它只负责创建 Flask 应用、注册路由、初始化数据库。

---

## 6. 数据模型设计

### 6.1 Content

统一内容模型，用于保存用户输入的一份原始内容。

字段：

- `id`
- `title`
- `summary`
- `body`
- `cover_image`
- `content_type`
- `tags`
- `created_at`
- `updated_at`

用途：

- 作为平台适配的原始输入
- 作为编辑和版本管理的基础对象

---

### 6.2 PlatformDraft

平台草稿是内容适配后的结果。

字段：

- `id`
- `content_id`
- `platform`
- `title`
- `summary`
- `body`
- `tags`
- `cover_image`
- `extra_config`
- `validation_warnings`
- `created_at`
- `updated_at`

用途：

- 展示某个平台的最终适配结果
- 支持预览和模拟发布
- 后续支持手工编辑和重新生成

---

### 6.3 PublishTask

发布任务记录一次模拟发布或真实发布。

字段：

- `id`
- `content_id`
- `platform_draft_id`
- `platform`
- `account_id`
- `mode`
- `status`
- `title`
- `error_message`
- `publish_url`
- `created_at`
- `started_at`
- `finished_at`

用途：

- 发布过程追踪
- 发布历史展示
- 后续扩展真实发布和重试机制

---

## 7. 平台适配层设计

平台适配器负责把统一内容转换为不同平台风格的草稿。

### 7.1 适配器职责

- 调整标题长度和风格
- 调整正文结构和语气
- 生成平台推荐标签
- 提示平台限制和格式问题
- 输出平台草稿对象

### 7.2 当前首批平台

- 公众号 `wechat_official`
- 知乎 `zhihu`
- B站 `bilibili`
- 小红书 `xiaohongshu`

### 7.3 适配器接口

```text
transform(content) -> platform_draft
```

### 7.4 设计原则

- 平台差异放在适配器里，不放在页面里
- 平台新增时只增加适配器，不修改核心业务流程
- 适配器优先返回可预览、可编辑的数据结构

---

## 8. 前端数据流

### 8.1 内容创建流程

```text
ContentEditor
  ↓ 调用 contentApi.create
后端保存 Content
  ↓
返回 content_id
  ↓
调用 contentApi.adapt
  ↓
生成 PlatformDraft
  ↓
跳转 AdaptationCenter
```

### 8.2 预览流程

```text
AdaptationCenter
  ↓ 获取 platform drafts
PreviewCenter
  ↓ 渲染平台样式
```

### 8.3 模拟发布流程

```text
PublishCenter
  ↓ 选择平台草稿
  ↓ 调用 publishApi.simulate
后端创建 PublishTask
  ↓
PublishHistory 展示结果
```

---

## 9. 后端业务流

### 9.1 内容创建

1. 前端提交原始内容
2. 后端校验标题和正文
3. 写入 `contents`
4. 返回创建结果

### 9.2 内容适配

1. 前端传入目标平台列表
2. 后端从 `contents` 读取原始内容
3. 根据平台选择适配器
4. 生成平台草稿并保存到 `platform_drafts`
5. 返回适配结果

### 9.3 模拟发布

1. 前端选择某个 `platform_draft`
2. 后端创建 `publish_tasks`
3. 任务状态标记为 `simulated`
4. 前端从历史接口查看结果

---

## 10. API 分层约定

所有接口统一采用：

```text
/api/...
```

返回格式统一为：

```json
{
  "code": 200,
  "msg": "success",
  "data": {}
}
```

建议的核心接口：

- `GET /api/health`
- `GET /api/platforms`
- `GET /api/contents`
- `POST /api/contents`
- `GET /api/contents/:id`
- `PUT /api/contents/:id`
- `POST /api/contents/:id/adapt`
- `GET /api/contents/:id/platform-drafts`
- `POST /api/publish/simulate`
- `GET /api/publish/tasks`

详细字段说明见 `docs/api.md`。

---

## 11. 扩展更多平台的方式

新增平台时遵循两层扩展：

### 11.1 先扩展适配器

在 `backend/adapters/` 新增一个平台适配器：

- 定义平台名称
- 定义标题和正文适配规则
- 定义平台提示和约束
- 返回统一草稿结构

### 11.2 再扩展真实发布器

后续如果接入真实发布，在发布层新增对应 Publisher：

- 登录逻辑
- 平台 Cookie
- 页面自动化
- 发布动作
- 成功失败回写

### 11.3 前端同步扩展

前端只需要从 `/api/platforms` 拉取平台配置，不需要硬编码平台逻辑。

---

## 12. 运行时数据

本项目的运行时数据建议放在：

```text
backend/data/
```

包括：

- SQLite 数据库
- 运行日志
- 临时导出数据
- 后续账号 Cookie 和素材

运行时数据不应直接提交到 Git。

---

## 13. 当前版本边界

当前版本重点是：

- 内容编辑
- 平台适配
- 平台草稿
- 预览
- 模拟发布

当前版本暂不重点实现：

- 公众号 / 知乎真实登录
- 浏览器自动化发布
- 复杂 AI 改写
- 复杂任务调度
- 多用户权限系统

这些能力会在 MVP 稳定后逐步加入。

---

## 14. 推荐开发顺序

1. 完善内容创建与列表
2. 完善平台适配器
3. 完善平台草稿预览
4. 完善模拟发布
5. 再接真实发布器
6. 最后再考虑 Tauri 桌面端

---

## 15. 总结

本项目采用“统一内容模型 + 平台适配器 + 平台草稿 + 模拟发布”的架构方式，把创作者的一份内容转换成多个平台可用的发布版本。前端负责输入、展示和预览，后端负责存储、适配和发布任务。通过分层设计，项目可以稳定地从 Web MVP 演进到可扩展的多平台发布系统。
