# API 文档 / Creator Content Publisher

## 1. 基础约定

### 1.1 Base URL

```text
http://127.0.0.1:5409/api
```

### 1.2 通用响应格式

成功：

```json
{
  "code": 200,
  "msg": "success",
  "data": {}
}
```

失败：

```json
{
  "code": 400,
  "msg": "错误原因",
  "data": null
}
```

### 1.3 统一数据模型

#### Content

```json
{
  "id": 1,
  "title": "标题",
  "summary": "摘要",
  "body": "正文",
  "cover_image": "",
  "video_path": "",
  "content_type": "article",
  "tags": ["AI", "效率工具"],
  "created_at": "2026-05-29 10:00:00",
  "updated_at": "2026-05-29 10:00:00"
}
```

#### PlatformDraft

```json
{
  "id": 1,
  "content_id": 1,
  "platform": "xiaohongshu",
  "title": "适配后的标题",
  "summary": "摘要",
  "body": "适配后的正文",
  "tags": ["AI", "效率工具"],
  "cover_image": "",
  "extra_config": {},
  "validation_warnings": [],
  "created_at": "2026-05-29 10:00:00",
  "updated_at": "2026-05-29 10:00:00"
}
```

#### PublishTask

```json
{
  "id": "uuid",
  "content_id": 1,
  "platform_draft_id": 1,
  "platform": "xiaohongshu",
  "account_id": null,
  "mode": "simulate",
  "status": "simulated",
  "title": "适配后的标题",
  "error_message": "",
  "publish_url": "",
  "external_id": "",
  "response_payload": {},
  "created_at": "2026-05-29 10:00:00",
  "started_at": "2026-05-29 10:00:00",
  "finished_at": "2026-05-29 10:00:00"
}
```

---

## 2. 健康检查

### GET /health

检查后端是否启动成功，同时返回平台列表摘要。

**Response**

```json
{
  "code": 200,
  "data": {
    "status": "ok",
    "database": "C:/Users/.../backend/data/app.db",
    "platforms": [
      { "key": "wechat_official", "name": "公众号", "description": "适合长文排版..." },
      { "key": "zhihu", "name": "知乎", "description": "适合理性分析..." }
    ]
  }
}
```

---

## 3. 平台接口

### GET /platforms

获取支持的平台列表。

**Response**

```json
{
  "code": 200,
  "data": [
    {
      "key": "wechat_official",
      "name": "公众号",
      "description": "适合长文排版、摘要和结构化表达。"
    },
    {
      "key": "zhihu",
      "name": "知乎",
      "description": "适合理性分析、问题导向和结构化论证。"
    }
  ]
}
```

---

## 4. 内容接口

### GET /contents

获取内容列表（按更新时间倒序）。

**Response**

```json
{
  "code": 200,
  "data": []
}
```

---

### POST /contents

创建内容。

**Request**

```json
{
  "title": "如何用 AI 提升创作效率",
  "summary": "一份面向创作者的效率指南",
  "body": "正文内容",
  "cover_image": "",
  "video_path": "",
  "content_type": "article",
  "tags": ["AI", "效率工具", "自媒体"]
}
```

**Response**

```json
{
  "code": 200,
  "data": {
    "id": 1,
    "title": "如何用 AI 提升创作效率"
  }
}
```

**规则**
- `title` 必填
- `body` 必填
- `tags` 为数组
- `content_type` 可选：`article`、`video`、`image_text`

---

### GET /contents/{content_id}

获取单条内容。

**Response**

```json
{
  "code": 200,
  "data": {
    "id": 1,
    "title": "如何用 AI 提升创作效率",
    "summary": "一份面向创作者的效率指南",
    "body": "正文内容",
    "cover_image": "",
    "video_path": "",
    "content_type": "article",
    "tags": ["AI", "效率工具", "自媒体"],
    "created_at": "2026-05-29 10:00:00",
    "updated_at": "2026-05-29 10:00:00"
  }
}
```

---

### PUT /contents/{content_id}

更新内容。

**Request**

```json
{
  "title": "更新后的标题",
  "summary": "更新后的摘要",
  "body": "更新后的正文",
  "cover_image": "",
  "video_path": "",
  "content_type": "article",
  "tags": ["AI", "效率"]
}
```

**Response**

```json
{
  "code": 200,
  "data": {}
}
```

---

### DELETE /contents/{content_id}

删除内容及其关联的平台草稿和发布任务。

**Response**

```json
{
  "code": 200,
  "data": true
}
```

---

### POST /contents/{content_id}/adapt

将统一内容适配成一个或多个平台草稿。

**Request**

```json
{
  "platforms": ["wechat_official", "zhihu", "bilibili", "xiaohongshu", "douyin", "kuaishou"]
}
```

**Response**

```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "content_id": 1,
      "platform": "xiaohongshu",
      "title": "AI提升创作效率",
      "summary": "一份面向创作者的效率指南",
      "body": "适配后的正文",
      "tags": ["AI", "效率工具"],
      "cover_image": "",
      "extra_config": {},
      "validation_warnings": []
    }
  ]
}
```

**说明**
- 未传 `platforms` 时，后端默认使用全部 6 个平台
- 适配器返回的平台草稿会写入 `platform_drafts` 表
- 不存在的平台 key 会被静默跳过

---

### GET /contents/{content_id}/platform-drafts

查询某条内容生成的所有平台草稿。

**Response**

```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "content_id": 1,
      "platform": "zhihu",
      "title": "知乎标题",
      "body": "知乎正文",
      "tags": ["AI"],
      "cover_image": "",
      "extra_config": {},
      "validation_warnings": []
    }
  ]
}
```

---

### PUT /platform-drafts/{draft_id}

更新平台草稿。

**Request**

```json
{
  "title": "修改后的标题",
  "summary": "修改后的摘要",
  "body": "修改后的正文",
  "tags": ["AI", "效率"],
  "cover_image": "",
  "extra_config": {
    "video_path": "C:/Videos/demo.mp4",
    "creation_declaration": "original"
  },
  "validation_warnings": []
}
```

**Response**

```json
{
  "code": 200,
  "data": {}
}
```

---

## 5. 发布接口

### POST /publish/simulate

模拟发布单个平台草稿。

**Request**

```json
{
  "platform_draft_id": 1
}
```

**Response**

```json
{
  "code": 200,
  "data": {
    "id": "uuid",
    "content_id": 1,
    "platform_draft_id": 1,
    "platform": "xiaohongshu",
    "mode": "simulate",
    "status": "simulated",
    "title": "AI提升创作效率",
    "publish_url": "",
    "created_at": "2026-05-29 10:00:00"
  }
}
```

---

### POST /publish/simulate-batch

批量模拟发布。

**Request**

```json
{
  "platform_draft_ids": [1, 2, 3]
}
```

**Response**

```json
{
  "code": 200,
  "data": [
    { "platform_draft_id": 1, "status": "simulated" },
    { "platform_draft_id": 2, "status": "simulated" },
    { "platform_draft_id": 3, "status": "failed", "error_message": "平台草稿不存在" }
  ]
}
```

---

### POST /publish/wechat/draft

保存到公众号草稿箱。

**Request**

```json
{
  "platform_draft_id": 1
}
```

**Response**

```json
{
  "code": 200,
  "data": {
    "task": {},
    "result": {
      "status": "published",
      "publish_url": "",
      "external_id": "media_id_xxx",
      "message": "草稿创建成功"
    }
  }
}
```

**前置条件**: 需在 `.env` 中配置 `WECHAT_APP_ID` 和 `WECHAT_APP_SECRET`。

---

### GET /publish/wechat/config

获取公众号发布配置状态。

**Response**

```json
{
  "code": 200,
  "data": {
    "app_id_configured": true,
    "app_secret_configured": true,
    "thumb_media_id_configured": false
  }
}
```

---

### GET /publish/wechat/token-check

检测微信 access_token 是否可用。

**Response**

```json
{
  "code": 200,
  "data": {
    "access_token_preview": "87_xxxxx...xxxxxx",
    "message": "access_token 获取成功"
  }
}
```

---

### POST /publish/zhihu/browser

知乎浏览器发布助手。打开知乎创作页并尝试填充标题、正文、话题、封面和创作声明。

**Request**

```json
{
  "platform_draft_id": 1,
  "auto_publish": false
}
```

**Response**

```json
{
  "code": 200,
  "data": {
    "task": { "id": "uuid", "status": "manual_pending" },
    "result": {
      "status": "manual_pending",
      "message": "请在知乎页面人工完成发布",
      "draft": { "title": "...", "body": "...", "tags": [] },
      "filled": ["标题", "正文", "话题"]
    }
  }
}
```

**说明**: 不会自动点击最终发布按钮。遇到登录、验证码或风控时停下等待人工处理。

---

### POST /publish/bilibili/browser

B站浏览器辅助发布。尝试上传视频、填充标题和简介。

**Request**

```json
{
  "platform_draft_id": 1,
  "auto_publish": true
}
```

**Response**

```json
{
  "code": 200,
  "data": {
    "task": { "id": "uuid", "status": "success" },
    "result": { "status": "draft_saved", "message": "已保存到B站草稿" }
  }
}
```

---

### POST /publish/douyin/browser

抖音浏览器辅助发布。尝试上传视频、填充标题、简介和话题标签。

**Request**

```json
{
  "platform_draft_id": 1,
  "auto_publish": true
}
```

**Response**

```json
{
  "code": 200,
  "data": {
    "task": { "id": "uuid", "status": "success" },
    "result": { "status": "published", "message": "发布成功" }
  }
}
```

---

### POST /publish/xiaohongshu/browser

小红书浏览器发布助手。尝试上传视频、填充标题/正文/话题、设置封面和内容声明。

**Request**

```json
{
  "platform_draft_id": 1
}
```

**Response**

```json
{
  "code": 200,
  "data": {
    "task": { "id": "uuid", "status": "manual_pending" },
    "result": {
      "status": "manual_pending",
      "message": "请在小红书页面人工完成发布",
      "draft": {
        "title": "...",
        "body": "...",
        "tags": [],
        "video_path": "",
        "thumbnail_path": "",
        "content_declaration": "",
        "original_declaration": ""
      },
      "filled": ["视频上传", "标题", "正文"]
    }
  }
}
```

---

### POST /publish/kuaishou/browser

快手浏览器发布助手。尝试上传视频、填充描述/标签、设置封面和作者声明。

**Request**

```json
{
  "platform_draft_id": 1
}
```

**Response**

```json
{
  "code": 200,
  "data": {
    "task": { "id": "uuid", "status": "manual_pending" },
    "result": {
      "status": "manual_pending",
      "message": "请在快手页面人工完成发布",
      "draft": {
        "title": "...",
        "body": "...",
        "tags": [],
        "video_path": "",
        "thumbnail_path": "",
        "author_declaration": ""
      },
      "filled": ["视频上传", "描述", "标签"]
    }
  }
}
```

---

### GET /publish/tasks

获取发布任务列表（按创建时间倒序）。

**Response**

```json
{
  "code": 200,
  "data": [
    {
      "id": "uuid",
      "platform": "xiaohongshu",
      "title": "AI提升创作效率",
      "mode": "simulate",
      "status": "simulated",
      "publish_url": "",
      "external_id": "",
      "created_at": "2026-05-29 10:00:00"
    }
  ]
}
```

---

### POST /publish/tasks/{task_id}/complete-manual

人工确认浏览器发布任务已完成。

**Request**

```json
{
  "publish_url": "https://..."
}
```

**Response**

```json
{
  "code": 200,
  "data": {
    "id": "uuid",
    "status": "success",
    "publish_url": "https://..."
  }
}
```

**说明**: 只能确认 `mode` 为 `browser` 或 `manual` 且状态为 `manual_pending` 的任务。`publish_url` 可选。

---

## 6. 发布模式说明

| mode | 含义 | status 取值 |
|------|------|-----------|
| `simulate` | 模拟发布 | `simulated` |
| `browser` | 浏览器辅助发布 | `pending` → `running` → `manual_pending` / `success` / `failed` |
| `wechat_draft` | 公众号 API 草稿 | `pending` → `running` → `success` / `failed` |
| `manual` | 手动发布 | `manual_pending` → `success` |

---

## 7. 错误码约定

| code | 含义 |
|------|------|
| 200 | 成功 |
| 400 | 参数错误 |
| 404 | 资源不存在 |
| 500 | 服务端错误 |

---

## 8. 接口总览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health` | 健康检查 |
| GET | `/api/platforms` | 平台列表 |
| GET | `/api/contents` | 内容列表 |
| POST | `/api/contents` | 创建内容 |
| GET | `/api/contents/{id}` | 获取内容 |
| PUT | `/api/contents/{id}` | 更新内容 |
| DELETE | `/api/contents/{id}` | 删除内容 |
| POST | `/api/contents/{id}/adapt` | 生成平台草稿 |
| GET | `/api/contents/{id}/platform-drafts` | 获取草稿列表 |
| PUT | `/api/platform-drafts/{id}` | 更新草稿 |
| POST | `/api/publish/simulate` | 模拟发布 |
| POST | `/api/publish/simulate-batch` | 批量模拟发布 |
| POST | `/api/publish/wechat/draft` | 公众号草稿发布 |
| GET | `/api/publish/wechat/config` | 公众号配置状态 |
| GET | `/api/publish/wechat/token-check` | 检测微信 Token |
| POST | `/api/publish/zhihu/browser` | 知乎浏览器发布 |
| POST | `/api/publish/bilibili/browser` | B站浏览器发布 |
| POST | `/api/publish/douyin/browser` | 抖音浏览器发布 |
| POST | `/api/publish/xiaohongshu/browser` | 小红书浏览器发布 |
| POST | `/api/publish/kuaishou/browser` | 快手浏览器发布 |
| GET | `/api/publish/tasks` | 发布任务列表 |
| POST | `/api/publish/tasks/{id}/complete-manual` | 确认手动发布完成 |
