from pathlib import Path

from playwright.sync_api import Error as PlaywrightError, sync_playwright


_sessions = []
DATA_DIR = Path(__file__).resolve().parents[1] / 'data' / 'browser'
XIAOHONGSHU_USER_DATA_DIR = DATA_DIR / 'xiaohongshu'


class XiaohongshuBrowserPublisher:
    creator_url = 'https://creator.xiaohongshu.com/publish/publish?from=homepage&target=video'

    def publish(self, draft, auto_publish=False):
        auto_publish = False
        context, page = self._open_browser_context()
        filled = []
        page.goto(self.creator_url, wait_until='domcontentloaded')
        page.wait_for_timeout(3000)

        blocking_reason = self._detect_blocking_reason(page)
        if blocking_reason == '登录状态异常':
            return self._manual_result(draft, filled, '小红书创作中心需要登录。请在打开的浏览器中手动登录后，再重新点击发布助手或人工补充内容。')
        if blocking_reason:
            return self._manual_result(draft, filled, f'小红书页面检测到{blocking_reason}，请在打开的浏览器中人工处理。')

        upload_state = 'no_video'
        if draft.get('video_path'):
            uploaded = self._try_upload_video(page, draft['video_path'], filled)
            if uploaded:
                upload_state = self._wait_until_upload_ready(page)
            else:
                upload_state = 'failed'

        self._fill_title(page, draft.get('title', ''), filled)
        self._fill_desc(page, draft.get('body') or draft.get('summary') or draft.get('title', ''), filled)
        self._fill_tags(page, draft.get('tags') or [], filled)
        self._try_apply_cover(page, draft.get('thumbnail_path') or draft.get('cover_image') or '', filled)
        self._try_set_content_declaration(page, draft.get('content_declaration', ''), filled)
        self._try_set_original_declaration(page, draft.get('original_declaration', ''), filled)

        blocking_reason = self._detect_blocking_reason(page)
        if blocking_reason:
            return self._manual_result(draft, filled, f'已尝试填充内容，但检测到{blocking_reason}，请在小红书页面人工处理。')
        if upload_state == 'failed':
            return self._manual_result(draft, filled, '检测到视频上传失败或未能选择视频文件，请在小红书页面人工重新上传。')
        if upload_state in ('uploading', 'unknown'):
            return self._manual_result(draft, filled, '视频可能仍在上传或处理中，请在小红书页面等待完成后人工发布。')
        if upload_state == 'no_video':
            return self._manual_result(draft, filled, '浏览器已打开小红书创作页并尝试填充内容，但未配置视频文件路径，请在小红书页面人工上传视频并发布。')

        self._wait_for_page_ready(page)
        return self._manual_result(draft, filled, '浏览器已打开小红书创作页并尝试上传视频、填充标题、正文、话题、封面和声明。请在小红书页面检查内容，并手动发布；系统不会自动点击最终发布按钮。')

    def _base_result(self, draft, filled):
        return {
            'creator_url': self.creator_url,
            'filled': filled,
            'draft': {
                'platform': 'xiaohongshu',
                'title': draft.get('title', ''),
                'body': draft.get('body', ''),
                'tags': draft.get('tags', []),
                'cover_image': draft.get('cover_image', ''),
                'video_path': draft.get('video_path', ''),
                'thumbnail_path': draft.get('thumbnail_path', ''),
                'content_declaration': draft.get('content_declaration', ''),
                'original_declaration': draft.get('original_declaration', ''),
            },
        }

    def _manual_result(self, draft, filled, message):
        return {
            **self._base_result(draft, filled),
            'status': 'manual_pending',
            'message': message,
        }

    def _open_browser_context(self):
        self._cleanup_closed_sessions()
        try:
            return self._launch_browser_context()
        except PlaywrightError:
            self._close_all_sessions()
            return self._launch_browser_context()

    def _launch_browser_context(self):
        XIAOHONGSHU_USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
        playwright = sync_playwright().start()
        try:
            context = playwright.chromium.launch_persistent_context(
                user_data_dir=str(XIAOHONGSHU_USER_DATA_DIR),
                headless=False,
                viewport=None,
            )
            page = context.pages[0] if context.pages else context.new_page()
            session = {'playwright': playwright, 'context': context, 'page': page}
            _sessions.append(session)
            return context, page
        except Exception:
            playwright.stop()
            raise

    def _cleanup_closed_sessions(self):
        for session in _sessions[:]:
            if self._session_is_alive(session):
                continue
            self._close_session(session)

    def _session_is_alive(self, session):
        page = session.get('page')
        context = session.get('context')
        try:
            if page and not page.is_closed():
                return True
            if context and context.pages:
                return any(not candidate.is_closed() for candidate in context.pages)
        except PlaywrightError:
            return False
        except Exception:
            return False
        return False

    def _close_all_sessions(self):
        for session in _sessions[:]:
            self._close_session(session)

    def _close_session(self, session):
        try:
            context = session.get('context')
            if context:
                context.close()
        except Exception:
            pass
        try:
            playwright = session.get('playwright')
            if playwright:
                playwright.stop()
        except Exception:
            pass
        try:
            _sessions.remove(session)
        except ValueError:
            pass

    def _try_upload_video(self, page, video_path, filled):
        path = Path(video_path).expanduser()
        if not path.exists() or not path.is_file():
            return False
        selectors = [
            "div[class^='upload-content'] input[class='upload-input']",
            'input.upload-input',
            'input[type="file"][accept*="video"]',
            'input[type="file"]',
        ]
        for selector in selectors:
            try:
                upload_input = page.locator(selector).first
                upload_input.wait_for(state='attached', timeout=5000)
                upload_input.set_input_files(str(path), timeout=10000)
                filled.append('视频文件')
                return True
            except Exception:
                continue
        return False

    def _wait_until_upload_ready(self, page):
        state = 'unknown'
        success_keywords = ['上传成功', '分辨率', '重新上传', '编辑封面', '已上传', '已选择', '100%']
        for _ in range(60):
            if self._visible_text(page, '上传失败'):
                return 'failed'
            try:
                publish_button = page.locator('xhs-publish-btn').first
                if publish_button.count() > 0 and publish_button.get_attribute('submit-disabled', timeout=800) == 'false':
                    return 'ready'
            except Exception:
                pass
            try:
                preview = page.locator("input.upload-input").first.locator('xpath=following-sibling::div[contains(@class, "preview-new")]')
                if preview.count() > 0:
                    text = preview.inner_text(timeout=1000)
                    if any(keyword in text for keyword in success_keywords):
                        return 'ready'
                    state = 'uploading'
            except Exception:
                pass
            if self._visible_text(page, '上传中') or self._visible_text(page, '处理中'):
                state = 'uploading'
            page.wait_for_timeout(2000)
        return state

    def _fill_title(self, page, title, filled):
        title = (title or '').strip()[:20]
        if not title:
            return False
        selectors = [
            'input[placeholder*="填写标题"]',
            'input[placeholder*="标题"]',
            'textarea[placeholder*="标题"]',
        ]
        for selector in selectors:
            try:
                locator = page.locator(selector).first
                locator.wait_for(state='visible', timeout=3000)
                locator.fill(title, timeout=3000)
                filled.append('标题')
                return True
            except Exception:
                continue
        return False

    def _fill_desc(self, page, body, filled):
        body = (body or '').strip()
        if not body:
            return False
        selectors = [
            'p[data-placeholder*="输入正文描述"]',
            '[contenteditable="true"][data-placeholder*="正文"]',
            '[contenteditable="true"][data-placeholder*="描述"]',
            '[contenteditable="true"]',
            'textarea[placeholder*="描述"]',
        ]
        for selector in selectors:
            try:
                locator = page.locator(selector).first
                locator.wait_for(state='visible', timeout=3000)
                locator.click(timeout=3000)
                page.keyboard.press('Control+A')
                page.keyboard.press('Delete')
                page.keyboard.insert_text(body)
                page.keyboard.press('Enter')
                filled.append('正文')
                return True
            except Exception:
                continue
        return False

    def _fill_tags(self, page, tags, filled):
        if not tags:
            return False
        try:
            desc = page.locator('p[data-placeholder*="输入正文描述"]').first
            if desc.is_visible(timeout=1000):
                desc.click(timeout=2000)
        except Exception:
            pass
        added = []
        for tag in tags[:10]:
            tag = str(tag).strip().lstrip('#')
            if not tag:
                continue
            try:
                page.keyboard.type('#' + tag, delay=30)
                topic = page.locator('#creator-editor-topic-container')
                topic.wait_for(state='visible', timeout=3000)
                topic.locator('.item').first.click(timeout=2000)
                added.append(tag)
            except Exception:
                try:
                    page.keyboard.type(' ', delay=10)
                    added.append(tag)
                except Exception:
                    continue
        if added:
            filled.append('话题')
            return True
        return False

    def _try_apply_cover(self, page, thumbnail_path, filled):
        thumbnail_path = (thumbnail_path or '').strip()
        if not thumbnail_path:
            return False
        cover_path = Path(thumbnail_path).expanduser()
        if not cover_path.exists() or not cover_path.is_file():
            return False
        try:
            cover_loc = page.locator('div[style*="background-image"]').first
            cover_loc.wait_for(state='attached', timeout=10000)
            cover_loc.hover(timeout=5000)
            page.wait_for_timeout(1000)
            page.locator('div.operator.pointer').first.click(force=True, timeout=5000)
        except Exception:
            for selector in ['button:has-text("封面")', '[role="button"]:has-text("封面")', 'text=编辑封面', 'text=修改封面']:
                try:
                    page.locator(selector).first.click(timeout=3000)
                    break
                except Exception:
                    continue
        modal_selectors = ['div.d-modal.cover-modal', 'div.cover-modal', 'div[class*="cover-modal"]', 'div.d-modal']
        modal = None
        for _ in range(2):
            page.wait_for_timeout(2000)
            for selector in modal_selectors:
                try:
                    candidate = page.locator(selector).first
                    if candidate.count() > 0:
                        modal = candidate
                        break
                except Exception:
                    continue
            if modal:
                break
        if not modal:
            return False
        try:
            file_input = modal.locator('input[type="file"][accept*="image"]').first
            file_input.wait_for(state='attached', timeout=10000)
            file_input.set_input_files(str(cover_path), timeout=10000)
            page.wait_for_timeout(3000)
            for selector in ['button.mojito-button:has-text("确定")', 'button:has-text("确定")', '.d-modal-footer button:has-text("确定")']:
                try:
                    modal.locator(selector).first.click(timeout=5000)
                    filled.append('封面')
                    return True
                except Exception:
                    continue
        except Exception:
            return False
        return False

    def _try_set_content_declaration(self, page, value, filled):
        value = (value or '').strip()
        if not value:
            return False
        try:
            trigger = page.locator('.d-select-placeholder:has-text("添加内容类型声明")').first
            if trigger.count() > 0:
                trigger.click(timeout=3000)
            else:
                page.locator('.d-select-wrapper').first.click(timeout=3000)
            page.wait_for_timeout(800)
            option = page.locator(f'.d-option .d-option-name:has-text("{value}")').first
            option.click(timeout=3000)
            filled.append('内容声明')
            return True
        except Exception:
            return False

    def _try_set_original_declaration(self, page, value, filled):
        value = str(value or '').strip().lower()
        if value not in ('true', '1', 'yes', 'original', '原创', '声明原创'):
            return False
        try:
            switch_card = page.locator('.custom-switch-card').filter(has_text='原创声明')
            switch = switch_card.locator('.d-switch').first
            switch.wait_for(state='visible', timeout=3000)
            classes = switch.get_attribute('class') or ''
            if 'd-switch-checked' not in classes:
                switch.click(timeout=3000)
                page.wait_for_timeout(1500)
            modal = page.locator('div.d-modal.d-modal-centered').first
            if modal.count() > 0:
                checkbox = modal.locator('.d-checkbox-simulator').first
                if checkbox.count() > 0:
                    checkbox.click(timeout=2000)
                    page.wait_for_timeout(500)
                confirm = modal.locator('button:has-text("声明原创")').first
                if confirm.count() > 0:
                    confirm.click(timeout=3000)
            filled.append('原创声明')
            return True
        except Exception:
            return False

    def _wait_for_page_ready(self, page):
        for _ in range(15):
            try:
                button = page.locator('xhs-publish-btn').first
                if button.count() > 0 and button.get_attribute('submit-disabled', timeout=800) == 'false':
                    return True
            except Exception:
                pass
            page.wait_for_timeout(1000)
        return False

    def _detect_blocking_reason(self, page):
        checks = [
            ('扫码登录', '登录状态异常'),
            ('请登录', '登录状态异常'),
            ('登录后', '登录状态异常'),
            ('验证码', '验证码或安全验证'),
            ('安全验证', '验证码或安全验证'),
            ('请完成验证', '验证码或安全验证'),
            ('风险', '平台风控提示'),
            ('异常', '平台风控提示'),
        ]
        if '/login' in page.url:
            return '登录状态异常'
        for text, reason in checks:
            if self._visible_text(page, text, 800):
                return reason
        return ''

    def _visible_text(self, page, text, timeout=800):
        try:
            return page.locator(f'text={text}').first.is_visible(timeout=timeout)
        except Exception:
            return False
