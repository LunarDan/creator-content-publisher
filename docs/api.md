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
  "created_at": "2026-05-29 10:00:00",
  "started_at": "2026-05-29 10:00:00",
  "finished_at": "2026-05-29 10:00:00"
}
```

---

## 2. 健康检查

### GET /health

检查后端是否启动成功，同时返回平台列表摘要。

#### Response

```json
{
  "code": 200,
  "data": {
    "status": "ok",
    "database": "C:/Users/.../backend/data/app.db",
    "platforms": []
  }
}
```

---

## 3. 平台接口

### GET /platforms

获取支持的平台列表。

#### Response

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

获取内容列表。

#### Response

```json
{
  "code": 200,
  "data": []
}
```

---

### POST /contents

创建内容。

#### Request

```json
{
  "title": "如何用 AI 提升创作效率",
  "summary": "一份面向创作者的效率指南",
  "body": "正文内容",
  "cover_image": "",
  "content_type": "article",
  "tags": ["AI", "效率工具", "自媒体"]
}
```

#### Response

```json
{
  "code": 200,
  "data": {
    "id": 1,
    "title": "如何用 AI 提升创作效率"
  }
}
```

#### 规则

- `title` 必填
- `body` 必填
- `tags` 为数组

---

### GET /contents/{content_id}

获取单条内容。

#### Response

```json
{
  "code": 200,
  "data": {
    "id": 1,
    "title": "如何用 AI 提升创作效率",
    "summary": "一份面向创作者的效率指南",
    "body": "正文内容",
    "cover_image": "",
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

#### Request

```json
{
  "title": "更新后的标题",
  "summary": "更新后的摘要",
  "body": "更新后的正文",
  "cover_image": "",
  "content_type": "article",
  "tags": ["AI", "效率"]
}
```

#### Response

```json
{
  "code": 200,
  "data": {}
}
```

---

### POST /contents/{content_id}/adapt

将统一内容适配成一个或多个平台草稿。

#### Request

```json
{
  "platforms": [
    "wechat_official",
    "zhihu",
    "bilibili",
    "xiaohongshu"
  ]
}
```

#### Response

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
      "extra_config": {
        "layout": "note",
        "tone": "friendly"
      },
      "validation_warnings": []
    }
  ]
}
```

#### 说明

- 未传 `platforms` 时，后端可使用默认平台集合。
- 适配器返回的平台草稿会写入 `platform_drafts` 表。

---

### GET /contents/{content_id}/platform-drafts

查询某条内容生成的所有平台草稿。

#### Response

```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "content_id": 1,
      "platform": "zhihu",
      "title": "知乎标题",
      "summary": "",
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

## 5. 发布接口

### POST /publish/simulate

模拟发布某个平台草稿。

#### Request

```json
{
  "platform_draft_id": 1
}
```

#### Response

```json
{
  "code": 200,
  "data": {
    "id": "e5b8b0e2-5e8c-49b4-90d8-5c2eb9d23e43",
    "content_id": 1,
    "platform_draft_id": 1,
    "platform": "xiaohongshu",
    "account_id": null,
    "mode": "simulate",
    "status": "simulated",
    "title": "AI提升创作效率",
    "error_message": "",
    "publish_url": "",
    "created_at": "2026-05-29 10:00:00",
    "started_at": "2026-05-29 10:00:00",
    "finished_at": "2026-05-29 10:00:00"
  }
}
```

---

### GET /publish/tasks

获取发布任务列表。

#### Response

```json
{
  "code": 200,
  "data": [
    {
      "id": "uuid",
      "platform": "xiaohongshu",
      "title": "AI提升创作效率",
      "mode": "simulate",
      "status": "simulated"
    }
  ]
}
```

---

## 6. 错误码约定

| code | 含义 |
| --- | --- |
| 200 | 成功 |
| 400 | 参数错误 |
| 404 | 资源不存在 |
| 500 | 服务端错误 |

---

## 7. 当前版本说明

当前版本先实现：

- 内容创建
- 平台适配
- 平台草稿保存
- 模拟发布
- 发布历史查询

后续可扩展：

- 真实发布
- 账号管理
- 平台登录
- 发布日志流
- AI 改写接口
