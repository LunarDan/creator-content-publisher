from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, sync_playwright


_sessions = []
DATA_DIR = Path(__file__).resolve().parents[1] / 'data' / 'browser'
ZHIHU_USER_DATA_DIR = DATA_DIR / 'zhihu'


class ZhihuBrowserPublisher:
    creator_url = 'https://zhuanlan.zhihu.com/write'
    fallback_url = 'https://www.zhihu.com/creator'

    def publish(self, draft, auto_publish=False):
        auto_publish = False
        ZHIHU_USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
        playwright = sync_playwright().start()
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(ZHIHU_USER_DATA_DIR),
            headless=False,
            viewport=None,
        )
        page = context.pages[0] if context.pages else context.new_page()
        _sessions.append({'playwright': playwright, 'context': context, 'page': page})

        filled = []
        page.goto(self.creator_url, wait_until='domcontentloaded')
        page.wait_for_timeout(3000)
        if not self._wait_for_editor(page):
            page.goto(self.fallback_url, wait_until='domcontentloaded')
            page.wait_for_timeout(3000)
            self._try_open_write_entry(page)
            self._wait_for_editor(page)

        blocking_reason = self._detect_blocking_reason(page)
        if blocking_reason:
            return self._manual_result(draft, filled, f'知乎页面检测到{blocking_reason}，请在打开的浏览器中人工处理；系统不会自动点击发布。')

        self._fill_title(page, draft.get('title', ''), filled)
        body = self._prepare_body(draft)
        self._fill_body(page, body, filled)
        self._try_fill_tags(page, draft.get('tags') or [], filled)
        self._try_apply_cover(page, draft.get('cover_image', ''), filled)
        self._try_select_creation_declaration(page, draft.get('creation_declaration', ''), filled)

        blocking_reason = self._detect_blocking_reason(page)
        if blocking_reason:
            return self._manual_result(draft, filled, f'已尝试填充内容，但检测到{blocking_reason}，请在知乎页面人工处理。')

        if auto_publish:
            result = self._try_final_publish(page)
            if result.get('status') == 'published':
                return {**self._base_result(draft, filled), **result}
            save_result = self._try_save_draft(page)
            if save_result.get('status') == 'draft_saved':
                return {**self._base_result(draft, filled), **save_result}
            return self._manual_result(draft, filled, result.get('message') or save_result.get('message') or '未能确认知乎发布成功，请人工确认。')

        return self._manual_result(draft, filled, '浏览器已打开知乎创作页并尝试填充标题、正文、话题、封面和创作声明。请在知乎页面检查内容，并手动保存草稿或发布。')

    def _base_result(self, draft, filled):
        return {
            'creator_url': self.creator_url,
            'filled': filled,
            'draft': {
                'platform': 'zhihu',
                'title': draft.get('title', ''),
                'body': draft.get('body', ''),
                'tags': draft.get('tags', []),
                'cover_image': draft.get('cover_image', ''),
                'creation_declaration': draft.get('creation_declaration', ''),
            },
        }

    def _manual_result(self, draft, filled, message):
        return {
            **self._base_result(draft, filled),
            'status': 'manual_pending',
            'message': message,
        }

    def _prepare_body(self, draft):
        body = draft.get('body') or draft.get('summary') or draft.get('title') or ''
        tags = draft.get('tags') or []
        if tags:
            body = f"{body}\n\n话题：{'、'.join(tags)}"
        return body

    def _wait_for_editor(self, page):
        selectors = [
            'textarea[placeholder*="标题"]',
            'input[placeholder*="标题"]',
            '[contenteditable="true"][data-placeholder*="标题"]',
            '[contenteditable="true"][placeholder*="标题"]',
            '.DraftEditor-editorContainer [contenteditable="true"]',
            '.ProseMirror[contenteditable="true"]',
            '[contenteditable="true"]',
        ]
        for _ in range(20):
            for selector in selectors:
                if self._is_visible(page, selector, 800):
                    return True
            page.wait_for_timeout(1000)
        return False

    def _try_open_write_entry(self, page):
        if self._detect_blocking_reason(page):
            return False
        selectors = [
            'a:has-text("写文章")',
            'button:has-text("写文章")',
            '[role="button"]:has-text("写文章")',
            'a:has-text("创作")',
            'button:has-text("创作")',
        ]
        for selector in selectors:
            try:
                locator = page.locator(selector).first
                locator.wait_for(state='visible', timeout=1200)
                locator.click(timeout=2000)
                page.wait_for_timeout(2000)
                return True
            except Exception:
                continue
        return False

    def _fill_title(self, page, title, filled):
        title = (title or '').strip()
        selectors = [
            'textarea[placeholder*="标题"]',
            'input[placeholder*="标题"]',
            '[contenteditable="true"][data-placeholder*="标题"]',
            '[contenteditable="true"][placeholder*="标题"]',
            '.WriteIndex-titleInput textarea',
        ]
        for selector in selectors:
            try:
                locator = page.locator(selector).first
                locator.wait_for(state='visible', timeout=1500)
                self._fill_locator(locator, title)
                filled.append('标题')
                return True
            except Exception:
                continue
        return False

    def _fill_body(self, page, body, filled):
        selectors = [
            '[contenteditable="true"][data-placeholder*="正文"]',
            '[contenteditable="true"][placeholder*="正文"]',
            '.RichText.Editable[contenteditable="true"]',
            '.DraftEditor-editorContainer [contenteditable="true"]',
            '.ProseMirror[contenteditable="true"]',
            '[contenteditable="true"]',
            'textarea[placeholder*="正文"]',
            'textarea',
        ]
        for selector in selectors:
            try:
                locator = page.locator(selector).last
                locator.wait_for(state='visible', timeout=1500)
                self._fill_locator(locator, body)
                filled.append('正文')
                return True
            except Exception:
                continue
        return False

    def _try_fill_tags(self, page, tags, filled):
        if not tags:
            return False
        selectors = [
            'input[placeholder*="话题"]',
            'input[placeholder*="添加话题"]',
            'input[placeholder*="标签"]',
        ]
        for selector in selectors:
            try:
                locator = page.locator(selector).first
                locator.wait_for(state='visible', timeout=1200)
                for tag in tags[:5]:
                    locator.fill(tag, timeout=1000)
                    page.keyboard.press('Enter')
                    page.wait_for_timeout(300)
                filled.append('话题')
                return True
            except Exception:
                continue
        return False

    def _try_apply_cover(self, page, cover_image, filled):
        cover_image = (cover_image or '').strip()
        if not cover_image:
            return False
        cover_path = Path(cover_image).expanduser()
        if not cover_path.exists() or not cover_path.is_file():
            return False
        triggers = [
            'button:has-text("封面")',
            '[role="button"]:has-text("封面")',
            'button:has-text("上传图片")',
            '[role="button"]:has-text("上传图片")',
            'button:has-text("添加图片")',
            '[role="button"]:has-text("添加图片")',
        ]
        for trigger in triggers:
            try:
                locator = page.locator(trigger).first
                locator.wait_for(state='visible', timeout=1000)
                locator.click(timeout=1500)
                page.wait_for_timeout(800)
                if self._set_first_file_input(page, cover_path):
                    filled.append('封面')
                    return True
            except Exception:
                continue
        if self._set_first_file_input(page, cover_path):
            filled.append('封面')
            return True
        return False

    def _set_first_file_input(self, page, file_path):
        try:
            file_input = page.locator('input[type="file"]').last
            file_input.set_input_files(str(file_path), timeout=2000)
            page.wait_for_timeout(1000)
            return True
        except Exception:
            return False

    def _try_select_creation_declaration(self, page, value, filled):
        value = (value or '').strip()
        if not value or value == 'no_label':
            return False
        option_texts = {
            'none': ['不声明', '无声明', '无需声明'],
            'no_label': ['不声明', '无声明', '无需声明'],
            'original': ['原创', '声明原创'],
            'repost': ['转载'],
            'authorized': ['授权转载', '授权'],
        }.get(value, [value])
        openers = ['创作声明', '声明', '原创', '转载']
        for opener_text in openers:
            if self._click_text(page, opener_text):
                page.wait_for_timeout(500)
                for option_text in option_texts:
                    if self._click_text(page, option_text):
                        filled.append('创作声明')
                        return True
        for option_text in option_texts:
            if self._click_text(page, option_text):
                filled.append('创作声明')
                return True
        return False

    def _click_text(self, page, text):
        selectors = [
            f'text={text}',
            f'button:has-text("{text}")',
            f'[role="button"]:has-text("{text}")',
            f'[role="option"]:has-text("{text}")',
            f'label:has-text("{text}")',
        ]
        for selector in selectors:
            try:
                locator = page.locator(selector).first
                locator.wait_for(state='visible', timeout=800)
                locator.click(timeout=1200)
                return True
            except Exception:
                continue
        return False

    def _try_save_draft(self, page):
        button = self._find_button(page, ['保存草稿', '存草稿'])
        if not button:
            return {'status': 'manual_pending', 'message': '未找到保存草稿按钮，请在知乎页面人工保存或发布。'}
        return self._click_and_detect(page, button, 'draft_saved')

    def _try_final_publish(self, page):
        blocking_reason = self._detect_blocking_reason(page)
        if blocking_reason:
            return {'status': 'manual_pending', 'message': f'检测到{blocking_reason}，请在知乎页面人工处理。'}
        button = self._find_button(page, ['发布'])
        if not button:
            return {'status': 'manual_pending', 'message': '未找到可点击的知乎发布按钮，请在知乎页面人工发布。'}
        return self._click_and_detect(page, button, 'published')

    def _find_button(self, page, texts):
        for text in texts:
            selectors = [
                f'button:has-text("{text}")',
                f'[role="button"]:has-text("{text}")',
                f'a:has-text("{text}")',
            ]
            for selector in selectors:
                try:
                    locator = page.locator(selector).first
                    locator.wait_for(state='visible', timeout=1200)
                    if locator.is_enabled(timeout=800):
                        return locator
                except Exception:
                    continue
        return None

    def _click_and_detect(self, page, button, success_status):
        try:
            button.scroll_into_view_if_needed(timeout=3000)
            button.click(timeout=3000)
            page.wait_for_timeout(4000)
        except Exception:
            return {'status': 'manual_pending', 'message': '已填充内容，但自动点击按钮失败，请在知乎页面人工确认。'}
        if self._detect_success(page):
            return {
                'status': success_status,
                'message': '已检测到知乎发布或保存成功提示。',
                'publish_url': page.url if success_status == 'published' else '',
            }
        return {'status': 'manual_pending', 'message': '已尝试操作，但未能确认知乎发布或保存成功，请人工确认。'}

    def _detect_success(self, page):
        for text in ['发布成功', '已发布', '保存成功', '草稿已保存', '内容管理', '创作中心']:
            if self._is_visible(page, f'text={text}', 1200):
                return True
        return any(part in page.url for part in ['/p/', '/creator/content', '/creator'])

    def _detect_blocking_reason(self, page):
        checks = [
            ('40362', '平台限制本次访问'),
            ('请求存在异常', '平台限制本次访问'),
            ('暂时限制本次访问', '平台限制本次访问'),
            ('私信知乎小管家', '平台限制本次访问'),
            ('扫码登录', '登录状态异常'),
            ('请登录', '登录状态异常'),
            ('登录后', '登录状态异常'),
            ('验证码', '验证码或安全验证'),
            ('安全验证', '验证码或安全验证'),
            ('请完成验证', '验证码或安全验证'),
            ('风险', '平台风控提示'),
            ('异常', '平台风控提示'),
            ('实名', '需要人工实名或账号验证'),
            ('绑定手机', '需要人工绑定或验证手机号'),
        ]
        for text, reason in checks:
            if self._is_visible(page, f'text={text}', 800):
                return reason
        return ''

    def _fill_locator(self, locator, value):
        try:
            locator.fill(value, timeout=3000)
            return True
        except Exception:
            locator.click(timeout=3000)
            locator.press('Control+A')
            locator.press('Delete')
            locator.type(value, delay=5)
            return True

    def _is_visible(self, page, selector, timeout=800):
        try:
            return page.locator(selector).first.is_visible(timeout=timeout)
        except Exception:
            return False
