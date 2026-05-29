# CLAUDE.md

This repository is a fresh Web-first MVP for a creator multi-platform content adaptation and publishing assistant.

## Project goal

Users input one source content item, and the system generates platform-specific drafts for platforms such as WeChat Official Account, Zhihu, Bilibili, and Xiaohongshu. The first version focuses on content modeling, platform adaptation, preview, simulated publish, and publish history.

## Architecture

```text
frontend/   Vue 3 + Vite UI
backend/    Flask + SQLite API
```

Planned backend layering:

```text
routes/         HTTP endpoints
services/       business orchestration
repositories/   SQLite access
adapters/       platform content adaptation
models/         domain objects
schemas/        request/response shapes
```

## Development rules

- Prefer a clean new implementation over carrying over legacy social-upload code.
- Keep the first release Web-first; add desktop packaging later.
- Keep simulated publish as the default early workflow.
- Add real platform publishing only after the content-adaptation pipeline is stable.
- Keep platform-specific logic isolated in adapters rather than hard-coding it in views.

## Expected backend responsibilities

- Initialize SQLite tables for contents, platform drafts, and publish tasks.
- Expose APIs for content CRUD, adaptation, platform draft retrieval, simulated publish, and history.
- Provide platform registration so new platforms can be added without rewriting the core flow.

## Expected frontend responsibilities

- Content editor
- Platform adaptation center
- Preview center
- Publish center
- Publish history
- Settings

## Notes

This repo is intentionally starting fresh; do not assume old `social-auto-upload-web-ui` files, routes, or publish flows remain valid.
