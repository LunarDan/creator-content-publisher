from pathlib import Path

from playwright.sync_api import sync_playwright


_sessions = []
DATA_DIR = Path(__file__).resolve().parents[1] / 'data' / 'browser'
DOUYIN_USER_DATA_DIR = DATA_DIR / 'douyin'


class DouyinBrowserPublisher:
    creator_url = 'https://creator.douyin.com/creator-micro/content/upload'

    def publish(self, draft, auto_publish=True):
        DOUYIN_USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
        playwright = sync_playwright().start()
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(DOUYIN_USER_DATA_DIR),
            headless=False,
            viewport=None,
        )
        page = context.pages[0] if context.pages else context.new_page()
        _sessions.append({'playwright': playwright, 'context': context, 'page': page})
        page.goto(self.creator_url, wait_until='domcontentloaded')
        page.wait_for_timeout(3000)

        filled = []
        blocking_reason = self._detect_blocking_reason(page)
        if blocking_reason == '登录状态异常':
            return self._manual_result(draft, filled, '抖音创作者中心需要登录。请在打开的浏览器中手动登录后，再检查内容并发布。')

        if draft.get('video_path'):
            uploaded = self._try_upload_video(page, draft['video_path'])
            if uploaded:
                filled.append('视频')
                self._wait_for_publish_form(page)
        else:
            self._wait_for_publish_form(page)

        self._fill_title_and_description(page, draft, filled)
        upload_state = self._wait_until_upload_ready(page)
        blocking_reason = self._detect_blocking_reason(page)
        if blocking_reason:
            return self._manual_result(draft, filled, f'已尝试填充内容，但检测到{blocking_reason}，请在抖音页面人工处理。')
        if upload_state == 'failed':
            return self._manual_result(draft, filled, '检测到视频上传失败，请在抖音页面人工重新上传。')
        if upload_state in ('uploading', 'unknown'):
            return self._manual_result(draft, filled, '视频可能仍在上传或处理，请在抖音页面等待完成后人工发布。')

        if auto_publish:
            publish_result = self._try_publish_until_done(page)
            if publish_result.get('status') == 'published':
                return {**self._base_result(draft, filled), **publish_result}
            return self._manual_result(draft, filled, publish_result.get('message', '未能确认抖音发布成功，请人工确认。'))

        return self._manual_result(draft, filled, '浏览器已打开并尝试上传和填充抖音内容。请在抖音页面人工检查并点击发布。')

    def _base_result(self, draft, filled):
        return {
            'creator_url': self.creator_url,
            'filled': filled,
            'draft': {
                'platform': 'douyin',
                'title': draft['title'],
                'body': draft['body'],
                'tags': draft.get('tags', []),
                'cover_image': draft.get('cover_image', ''),
                'video_path': draft.get('video_path', ''),
            },
        }

    def _manual_result(self, draft, filled, message):
        return {
            **self._base_result(draft, filled),
            'status': 'manual_pending',
            'message': message,
        }

    def _try_upload_video(self, page, video_path):
        try:
            path = Path(video_path).expanduser()
            if not path.exists():
                return False
            selectors = [
                "div[class^='container'] input",
                'input[type="file"]',
            ]
            for selector in selectors:
                try:
                    upload_input = page.locator(selector).first
                    upload_input.set_input_files(str(path), timeout=5000)
                    return True
                except Exception:
                    continue
        except Exception:
            return False
        return False

    def _wait_for_publish_form(self, page):
        for _ in range(40):
            if any(part in page.url for part in ['/creator-micro/content/publish', '/creator-micro/content/post/video']):
                return True
            for selector in ['text=作品描述', '.zone-container[contenteditable="true"]', '[contenteditable="true"]']:
                try:
                    if page.locator(selector).first.is_visible(timeout=800):
                        return True
                except Exception:
                    continue
            page.wait_for_timeout(1500)
        return False

    def _fill_title_and_description(self, page, draft, filled):
        title = (draft.get('title') or '')[:30]
        body = draft.get('body') or draft.get('summary') or title
        tags = draft.get('tags') or []
        description = body
        if tags:
            description = f"{description}\n\n{' '.join('#' + tag for tag in tags)}"

        if self._fill_title(page, title):
            filled.append('标题')
        if self._fill_description(page, description):
            filled.append('简介/话题')

    def _fill_title(self, page, title):
        selectors = [
            'div:has-text("作品描述") input[type="text"]',
            'input[placeholder*="标题"]',
            'input[placeholder*="填写标题"]',
            'input[type="text"]',
        ]
        for selector in selectors:
            try:
                locator = page.locator(selector).first
                locator.wait_for(state='visible', timeout=1500)
                locator.fill(title, timeout=3000)
                return True
            except Exception:
                continue
        return False

    def _fill_description(self, page, description):
        selectors = [
            '.zone-container[contenteditable="true"]',
            '[contenteditable="true"]',
            'textarea[placeholder*="描述"]',
            'textarea[placeholder*="简介"]',
        ]
        for selector in selectors:
            try:
                locator = page.locator(selector).first
                locator.wait_for(state='visible', timeout=1500)
                locator.click(timeout=3000)
                page.keyboard.press('Control+A')
                page.keyboard.press('Delete')
                page.keyboard.insert_text(description)
                return True
            except Exception:
                continue
        return False

    def _wait_until_upload_ready(self, page):
        state = 'unknown'
        for _ in range(60):
            if self._is_visible(page, '[class^="long-card"] div:has-text("重新上传")'):
                return 'ready'
            if self._is_visible(page, 'div.progress-div > div:has-text("上传失败")') or self._is_visible(page, 'text=上传失败'):
                return 'failed'
            blocking_reason = self._detect_blocking_reason(page)
            if blocking_reason in ('视频仍在上传中', '视频仍在处理中'):
                state = 'uploading'
                page.wait_for_timeout(2000)
                continue
            if self._find_publish_button(page):
                return 'ready'
            page.wait_for_timeout(2000)
        return state

    def _try_publish_until_done(self, page):
        for _ in range(30):
            publish_result = self._try_publish(page)
            if publish_result.get('status') == 'published':
                return publish_result
            if self._handle_auto_video_cover(page):
                page.wait_for_timeout(1000)
                continue
            if '没有找到可点击的发布按钮' in publish_result.get('message', ''):
                page.wait_for_timeout(1000)
                continue
            return publish_result
        return {
            'status': 'manual_pending',
            'message': '已多次尝试发布，但未能确认抖音发布成功，请人工确认。',
        }

    def _try_publish(self, page):
        blocking_reason = self._detect_blocking_reason(page)
        if blocking_reason:
            return {
                'status': 'manual_pending',
                'message': f'已填充内容，但检测到{blocking_reason}，请在抖音页面人工处理后发布。',
            }
        button = self._find_publish_button(page)
        if not button:
            return {
                'status': 'manual_pending',
                'message': '已填充内容，但没有找到可点击的发布按钮，请在抖音页面人工确认发布。',
            }
        try:
            button.scroll_into_view_if_needed(timeout=5000)
            button.click(timeout=5000)
            page.wait_for_timeout(5000)
        except Exception:
            return {
                'status': 'manual_pending',
                'message': '已填充内容，但自动点击发布按钮失败，请在抖音页面人工确认发布。',
            }
        if self._detect_success(page):
            return {
                'status': 'published',
                'message': '已尝试自动发布，并检测到抖音发布成功或进入内容管理页。',
                'publish_url': '',
            }
        blocking_reason = self._detect_blocking_reason(page)
        if blocking_reason:
            return {
                'status': 'manual_pending',
                'message': f'已尝试发布，但检测到{blocking_reason}，请在抖音页面人工处理。',
            }
        return {
            'status': 'manual_pending',
            'message': '已尝试发布，但未能确认抖音发布成功，请人工确认。',
        }

    def _find_publish_button(self, page):
        selectors = [
            'button:has-text("发布")',
            'button:has-text("立即发布")',
            '[role="button"]:has-text("发布")',
            '[role="button"]:has-text("立即发布")',
        ]
        for selector in selectors:
            try:
                locator = page.locator(selector).filter(has_not_text='定时').first
                locator.wait_for(state='visible', timeout=1200)
                if locator.is_enabled(timeout=800):
                    return locator
            except Exception:
                continue
        return None

    def _detect_success(self, page):
        success_texts = ['发布成功', '作品发布成功', '内容管理', '作品管理']
        for text in success_texts:
            if self._is_visible(page, f'text={text}', 1200):
                return True
        return '/creator-micro/content/manage' in page.url

    def _detect_blocking_reason(self, page):
        checks = [
            ('扫码登录', '登录状态异常'),
            ('请先登录', '登录状态异常'),
            ('验证码', '验证码或安全验证'),
            ('安全验证', '验证码或安全验证'),
            ('风险', '平台风控提示'),
            ('风控', '平台风控提示'),
            ('上传失败', '视频上传失败'),
            ('上传中', '视频仍在上传中'),
            ('处理中', '视频仍在处理中'),
            ('请设置封面', '需要人工设置封面'),
            ('请选择封面', '需要人工设置封面'),
            ('请选择', '必填项未完成'),
            ('必填', '必填项未完成'),
        ]
        for text, reason in checks:
            if self._is_visible(page, f'text={text}', 800):
                return reason
        return ''

    def _handle_auto_video_cover(self, page):
        if not self._is_visible(page, 'text=请设置封面', 1000) and not self._is_visible(page, 'text=请选择封面', 1000):
            return False
        selectors = [
            'text=选择封面',
            'button:has-text("选择封面")',
            '[role="button"]:has-text("选择封面")',
        ]
        for selector in selectors:
            try:
                page.locator(selector).first.click(timeout=2000)
                page.wait_for_timeout(1000)
                break
            except Exception:
                continue
        for selector in ['text=推荐封面', 'text=完成', 'button:has-text("完成")']:
            try:
                locator = page.locator(selector).first
                locator.click(timeout=2000)
                page.wait_for_timeout(1000)
            except Exception:
                continue
        return True

    def _is_visible(self, page, selector, timeout=800):
        try:
            return page.locator(selector).first.is_visible(timeout=timeout)
        except Exception:
            return False
