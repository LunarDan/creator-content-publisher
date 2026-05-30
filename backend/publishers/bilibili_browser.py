from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, sync_playwright


_sessions = []
DATA_DIR = Path(__file__).resolve().parents[1] / 'data' / 'browser'
BILIBILI_USER_DATA_DIR = DATA_DIR / 'bilibili'


class BilibiliBrowserPublisher:
    creator_url = 'https://member.bilibili.com/platform/upload/video/frame'

    def publish(self, draft, auto_publish=True):
        BILIBILI_USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
        playwright = sync_playwright().start()
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(BILIBILI_USER_DATA_DIR),
            headless=False,
            viewport=None,
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(self.creator_url, wait_until='domcontentloaded')
        page.wait_for_timeout(3000)
        _sessions.append({'playwright': playwright, 'context': context, 'page': page})

        if draft.get('video_path'):
            self._try_upload_video(page, draft['video_path'])
            self._wait_for_publish_form(page)
        else:
            self._wait_for_publish_form(page)

        filled = []
        self._fill_title(page, draft['title'], filled)
        self._fill_description(page, draft['body'], filled)

        result = {
            'creator_url': self.creator_url,
            'status': 'manual_pending',
            'filled': filled,
            'message': '浏览器已打开并保持登录态。请在 B站页面确认内容、保存草稿或发布；如果页面结构变化，可能需要手动补充。',
            'draft': {
                'title': draft['title'],
                'body': draft['body'],
                'tags': draft.get('tags', []),
                'cover_image': draft.get('cover_image', ''),
                'video_path': draft.get('video_path', ''),
                'creation_declaration': draft.get('creation_declaration', ''),
            },
        }
        if auto_publish:
            save_result = self._try_save_draft(page)
            result.update(save_result)
        return result

    def _try_save_draft(self, page):
        self._wait_until_video_ready(page)
        button = self._find_save_draft_button(page)
        if not button:
            return {
                'status': 'manual_pending',
                'message': '已填充标题和简介，但没有找到可点击的保存草稿按钮，请在 B站页面人工保存草稿。',
            }

        try:
            button.scroll_into_view_if_needed(timeout=5000)
            if not self._click_locator_by_coordinates(page, button):
                button.click(timeout=5000)
            page.wait_for_timeout(5000)
        except Exception:
            return {
                'status': 'manual_pending',
                'message': '已填充标题和简介，但自动点击保存草稿失败，请在 B站页面人工保存草稿。',
            }

        if self._detect_draft_saved(page):
            return {
                'status': 'draft_saved',
                'message': '已填充标题和简介，并检测到 B站草稿保存成功提示。',
                'publish_url': '',
            }

        blocking_reason = self._detect_blocking_reason(page)
        if blocking_reason:
            return {
                'status': 'manual_pending',
                'message': f'已尝试保存草稿，但检测到{blocking_reason}，请在 B站页面人工处理。',
            }
        return {
            'status': 'manual_pending',
            'message': '已尝试保存草稿，但未能确认保存成功，请在 B站页面人工确认。',
        }

    def _wait_until_video_ready(self, page):
        for _ in range(60):
            blocking_reason = self._detect_blocking_reason(page)
            if blocking_reason not in ('视频仍在上传中', '视频仍在处理中'):
                return
            page.wait_for_timeout(2000)

    def _find_save_draft_button(self, page):
        selectors = [
            'button:has-text("存草稿")',
            'button:has-text("保存草稿")',
            'button:has-text("保存为草稿")',
            '[role="button"]:has-text("存草稿")',
            '[role="button"]:has-text("保存草稿")',
            '[role="button"]:has-text("保存为草稿")',
            'div:has-text("存草稿")',
            'div:has-text("保存草稿")',
            'span:has-text("存草稿")',
            'span:has-text("保存草稿")',
            '.submit-add:has-text("存草稿")',
            '.submit-add:has-text("保存草稿")',
        ]
        for selector in selectors:
            try:
                locator = page.locator(selector).filter(has_not_text='发布').filter(has_not_text='投稿').last
                locator.wait_for(state='visible', timeout=1500)
                if locator.is_enabled(timeout=1000):
                    return locator
            except Exception:
                continue
        return None

    def _click_locator_by_coordinates(self, page, locator):
        try:
            box = locator.bounding_box(timeout=2000)
            if not box:
                return False
            x = box['x'] + box['width'] / 2
            y = box['y'] + box['height'] / 2
            page.mouse.move(x, y)
            page.wait_for_timeout(100)
            page.mouse.down()
            page.wait_for_timeout(80)
            page.mouse.up()
            page.wait_for_timeout(500)
            return True
        except Exception:
            return False

    def _detect_draft_saved(self, page):
        success_texts = ['保存草稿成功', '草稿保存成功', '保存成功', '已保存草稿', '已存入草稿']
        for text in success_texts:
            try:
                if page.locator(f'text={text}').first.is_visible(timeout=1500):
                    return True
            except Exception:
                continue
        return False

    def _try_final_publish(self, page):
        blocking_reason = self._detect_blocking_reason(page)
        if blocking_reason:
            return {
                'status': 'manual_pending',
                'message': f'已填充内容，但检测到{blocking_reason}，请在 B站页面人工处理后发布。',
            }

        button = self._find_publish_button(page)
        if not button:
            return {
                'status': 'manual_pending',
                'message': '已填充内容，但没有找到可点击的发布按钮，请在 B站页面人工确认发布。',
            }

        try:
            button.scroll_into_view_if_needed(timeout=5000)
            button.click(timeout=5000)
            page.wait_for_timeout(5000)
        except Exception:
            return {
                'status': 'manual_pending',
                'message': '已填充内容，但自动点击发布按钮失败，请在 B站页面人工确认发布。',
            }

        if self._detect_success(page):
            return {
                'status': 'published',
                'message': '已尝试自动发布，并检测到发布成功提示。',
                'publish_url': '',
            }

        blocking_reason = self._detect_blocking_reason(page)
        if blocking_reason:
            return {
                'status': 'manual_pending',
                'message': f'已尝试自动发布，但检测到{blocking_reason}，请在 B站页面人工处理。',
            }
        return {
            'status': 'manual_pending',
            'message': '已尝试自动发布，但未能确认发布成功，请在 B站页面人工确认。',
        }

    def _detect_blocking_reason(self, page):
        checks = [
            ('验证码', '验证码或安全验证'),
            ('安全验证', '验证码或安全验证'),
            ('风险', '平台风控提示'),
            ('请先登录', '登录状态异常'),
            ('登录', '登录状态异常'),
            ('上传中', '视频仍在上传中'),
            ('处理中', '视频仍在处理中'),
            ('请选择创作声明', '创作声明未完成'),
            ('创作声明不能为空', '创作声明未完成'),
            ('请选择内容无需标注', '创作声明未完成'),
            ('请选择', '必填项未完成'),
            ('必选', '必填项未完成'),
        ]
        for text, reason in checks:
            try:
                if page.locator(f'text={text}').first.is_visible(timeout=800):
                    return reason
            except Exception:
                continue
        return ''

    def _find_publish_button(self, page):
        selectors = [
            'button:has-text("立即发布")',
            'button:has-text("发布")',
            'button:has-text("立即投稿")',
            'button:has-text("投稿")',
            '[role="button"]:has-text("立即发布")',
            '[role="button"]:has-text("发布")',
            '[role="button"]:has-text("立即投稿")',
            '[role="button"]:has-text("投稿")',
            '.submit-add:has-text("发布")',
        ]
        for selector in selectors:
            try:
                locator = page.locator(selector).filter(has_not_text='保存').filter(has_not_text='草稿').first
                locator.wait_for(state='visible', timeout=1500)
                if locator.is_enabled(timeout=1000):
                    return locator
            except Exception:
                continue
        return None

    def _detect_success(self, page):
        success_texts = ['发布成功', '投稿成功', '提交成功', '稿件管理', '内容管理']
        for text in success_texts:
            try:
                if page.locator(f'text={text}').first.is_visible(timeout=1500):
                    return True
            except Exception:
                continue
        return any(part in page.url for part in ['/platform/upload-manager', '/platform/video-manage', '/platform/content'])

    def _try_upload_video(self, page, video_path):
        try:
            path = Path(video_path).expanduser()
            if not path.exists():
                return
            upload_input = page.locator('input[type="file"]').first
            upload_input.set_input_files(str(path))
        except Exception:
            return

    def _wait_for_publish_form(self, page):
        try:
            page.locator('input, textarea, [contenteditable="true"]').first.wait_for(state='visible', timeout=60000)
        except PlaywrightTimeoutError:
            return

    def _fill_title(self, page, title, filled):
        selectors = [
            'input[placeholder*="标题"]',
            'textarea[placeholder*="标题"]',
            '.title input',
            '.video-title input',
            '[class*="title"] input',
        ]
        for selector in selectors:
            try:
                locator = page.locator(selector).first
                locator.wait_for(state='visible', timeout=5000)
                locator.click(timeout=5000)
                locator.press('Control+A')
                locator.type(title, delay=10, timeout=10000)
                filled.append('标题')
                return
            except PlaywrightTimeoutError:
                continue
            except Exception:
                continue
        self._try_fill_near_label(page, ['标题'], title, filled, '标题')

    def _fill_description(self, page, body, filled):
        selectors = [
            'textarea[placeholder*="简介"]',
            'textarea[placeholder*="描述"]',
            'textarea[placeholder*="介绍"]',
            '[contenteditable="true"][placeholder*="简介"]',
            '[contenteditable="true"][data-placeholder*="简介"]',
            '[contenteditable="true"][aria-label*="简介"]',
            '.ql-editor[contenteditable="true"]',
            '.bili-rich-textarea [contenteditable="true"]',
            '.video-desc [contenteditable="true"]',
            '[class*="desc"] [contenteditable="true"]',
            '[class*="description"] [contenteditable="true"]',
            '[class*="intro"] [contenteditable="true"]',
            '[class*="desc"] textarea',
            '[class*="description"] textarea',
            '[class*="intro"] textarea',
        ]
        if self._try_fill(page, selectors, body, filled, '简介'):
            return
        self._try_fill_near_label(page, ['简介', '作品简介', '视频简介', '描述', '介绍'], body, filled, '简介')

    def _try_fill(self, page, selectors, value, filled, label):
        for selector in selectors:
            try:
                locator = page.locator(selector).first
                locator.wait_for(state='visible', timeout=5000)
                self._fill_locator(locator, value)
                filled.append(label)
                return True
            except PlaywrightTimeoutError:
                continue
            except Exception:
                continue
        return False

    def _try_fill_near_label(self, page, labels, value, filled, field_label):
        for label in labels:
            locators = [
                page.locator(f'text={label}').locator('xpath=ancestor::*[self::div or self::section][1]').locator('textarea, [contenteditable="true"]').first,
                page.locator(f'text={label}').locator('xpath=ancestor::*[self::div or self::section][1]/following-sibling::*[1]//textarea | ancestor::*[self::div or self::section][1]/following-sibling::*[1]//*[@contenteditable="true"]').first,
                page.locator(f'xpath=//*[contains(normalize-space(), "{label}")]/following::textarea[1] | //*[contains(normalize-space(), "{label}")]/following::*[@contenteditable="true"][1]').first,
            ]
            for locator in locators:
                try:
                    locator.wait_for(state='visible', timeout=3000)
                    self._fill_locator(locator, value)
                    filled.append(field_label)
                    return True
                except PlaywrightTimeoutError:
                    continue
                except Exception:
                    continue
        return False

    def _select_creation_declaration(self, page, value, filled):
        value = value or 'no_label'
        value_map = {
            'no_label': ['内容无需标注', '无需标注'],
            'original': ['原创', '自制'],
            'repost': ['转载'],
        }
        candidates = value_map.get(value, value_map['no_label'])

        try:
            trigger = page.locator('input.bco-select-input-inner, input.bcc-select-input-inner, input[placeholder*="创作声明"]').first
            trigger.wait_for(state='visible', timeout=5000)
            trigger.scroll_into_view_if_needed(timeout=3000)
            trigger.click(timeout=3000)
            page.wait_for_timeout(300)
            if self._declaration_selected(page, candidates[0]):
                filled.append('创作声明')
                return True
        except Exception:
            return False

        for candidate in candidates:
            if self._click_declaration_option_by_coordinates(page, candidate):
                filled.append('创作声明')
                return True

            option_locators = [
                page.locator(f'.bee-select-list-wrap li.beo-option:has-text("{candidate}")').first,
                page.locator(f'.bce-select-list-wrap li.beo-option:has-text("{candidate}")').first,
                page.locator(f'.bee-select-list-wrap li.bee-option:has-text("{candidate}")').first,
                page.locator(f'.bce-select-list-wrap li.bee-option:has-text("{candidate}")').first,
                page.locator(f'li.beo-option:has-text("{candidate}")').first,
                page.locator(f'li.bee-option:has-text("{candidate}")').first,
                page.locator(f'article.option-hover-tips:has-text("{candidate}")').first,
            ]
            for locator in option_locators:
                try:
                    locator.wait_for(state='visible', timeout=3000)
                    locator.scroll_into_view_if_needed(timeout=2000)
                    locator.evaluate(
                        """
                        (element) => {
                            const target = element.closest('li, article, div') || element;
                            target.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true, view: window }));
                            target.dispatchEvent(new MouseEvent('mouseup', { bubbles: true, cancelable: true, view: window }));
                            target.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
                        }
                        """
                    )
                    page.wait_for_timeout(300)
                    if self._declaration_selected(page, candidate):
                        filled.append('创作声明')
                        return True
                    locator.click(timeout=3000, force=True)
                    page.wait_for_timeout(300)
                    if self._declaration_selected(page, candidate):
                        filled.append('创作声明')
                        return True
                except Exception:
                    continue
        if self._select_declaration_with_keyboard(page, trigger, candidates):
            filled.append('创作声明')
            return True
        return False

    def _click_declaration_option_by_coordinates(self, page, candidate):
        option_selectors = [
            f'.bee-select-list-wrap li.beo-option:has-text("{candidate}")',
            f'.bce-select-list-wrap li.beo-option:has-text("{candidate}")',
            f'.bee-select-list-wrap article.option-hover-tips:has-text("{candidate}") li',
            f'.bce-select-list-wrap article.option-hover-tips:has-text("{candidate}") li',
            f'article.option-hover-tips:has-text("{candidate}") li',
            f'li.beo-option:has-text("{candidate}")',
            f'li.bee-option:has-text("{candidate}")',
        ]
        for selector in option_selectors:
            try:
                option = page.locator(selector).first
                option.wait_for(state='visible', timeout=2000)
                option.scroll_into_view_if_needed(timeout=2000)
                box = option.bounding_box(timeout=2000)
                if not box:
                    continue
                x = box['x'] + box['width'] / 2
                y = box['y'] + box['height'] / 2
                page.mouse.move(x, y)
                page.wait_for_timeout(100)
                page.mouse.down()
                page.wait_for_timeout(80)
                page.mouse.up()
                page.wait_for_timeout(500)
                if self._declaration_selected(page, candidate):
                    return True
            except Exception:
                continue
        return False

    def _select_declaration_with_keyboard(self, page, trigger, candidates):
        try:
            trigger.click(timeout=3000)
            page.wait_for_timeout(300)
            for key in ['Home', 'Enter', 'ArrowDown', 'Enter']:
                page.keyboard.press(key)
                page.wait_for_timeout(200)
                for candidate in candidates:
                    if self._declaration_selected(page, candidate):
                        return True
            trigger.click(timeout=3000)
            page.wait_for_timeout(300)
            trigger.press('ArrowDown')
            page.wait_for_timeout(200)
            trigger.press('Enter')
            page.wait_for_timeout(300)
            return any(self._declaration_selected(page, candidate) for candidate in candidates)
        except Exception:
            return False

    def _declaration_selected(self, page, candidate):
        try:
            value = page.locator('input.bco-select-input-inner, input.bcc-select-input-inner, input[placeholder*="创作声明"]').first.input_value(timeout=1000)
            return candidate in value
        except Exception:
            return False

    def _fill_locator(self, locator, value):
        locator.scroll_into_view_if_needed(timeout=5000)
        locator.click(timeout=5000)
        locator.press('Control+A')
        locator.type(value, delay=10, timeout=20000)
        locator.evaluate(
            """
            (element, text) => {
                if (element.isContentEditable) {
                    element.focus();
                    if (!element.innerText || element.innerText.trim() !== text.trim()) {
                        element.innerText = text;
                    }
                } else if ('value' in element && element.value !== text) {
                    element.value = text;
                }
                element.dispatchEvent(new InputEvent('input', { bubbles: true, inputType: 'insertText', data: text }));
                element.dispatchEvent(new Event('change', { bubbles: true }));
                element.dispatchEvent(new Event('blur', { bubbles: true }));
            }
            """,
            value,
        )
