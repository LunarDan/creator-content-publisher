# Creator Content Publisher

创作者多平台内容发布助手。项目目标是让创作者输入一份原始内容，系统自动生成公众号、知乎、B站、小红书等平台的适配草稿，并支持预览、模拟发布与后续真实发布扩展。

## 当前版本

这是一个全新初始化的 Web-first MVP，不依赖旧项目代码。

已包含：

- Vue 3 + Vite 前端
- Flask + SQLite 后端
- 统一内容模型
- 平台适配器架构
- 公众号 / 知乎 / B站 / 小红书模拟适配
- 平台草稿预览
- 模拟发布任务
- 发布历史

## 技术栈

| 层级 | 技术 |
| --- | --- |
| Frontend | Vue 3, Vite, Vue Router, Pinia, Element Plus |
| Backend | Python, Flask, SQLite |
| Publish Mode | Simulated first, real publishing later |

## 项目结构

```text
backend/
  app.py                  Flask 入口
  db.py                   SQLite 连接与行转换
  init_db.py              数据库初始化
  routes/                 HTTP 路由
  services/               业务服务
  repositories/           数据访问
  adapters/               平台内容适配器

frontend/
  src/api/                API 请求封装
  src/stores/             Pinia 状态
  src/views/              页面
  src/router/             路由
  src/styles/             样式
```

## 快速开始

### 后端

```bash
cd backend
pip install -r requirements.txt
python app.py
```

默认地址：`http://127.0.0.1:5409`

### 前端

```bash
cd frontend
npm install
npm run dev
```

默认地址：`http://127.0.0.1:5173`

### 构建前端

```bash
cd frontend
npm run build
```

## MVP 使用流程

1. 在内容创作页创建内容。
2. 选择目标平台。
3. 生成平台适配草稿。
4. 在预览中心查看各平台版本。
5. 在发布中心执行模拟发布。
6. 在发布历史查看任务结果。

## 平台扩展设计

新增平台分两步：

1. 在 `backend/adapters/` 中实现内容适配器。
2. 后续在真实发布阶段新增 Publisher，用于对接平台 API 或浏览器自动化。

适配器负责：

- 标题风格调整
- 正文格式转换
- 标签生成
- 平台限制校验
- 预览数据生成

真实发布能力会在模拟发布稳定后逐步接入。
