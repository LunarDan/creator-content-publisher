from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, sync_playwright


_sessions = []
DATA_DIR = Path(__file__).resolve().parents[1] / 'data' / 'browser'
BILIBILI_USER_DATA_DIR = DATA_DIR / 'bilibili'


class BilibiliBrowserPublisher:
    creator_url = 'https://member.bilibili.com/platform/upload/video/frame'

    def publish(self, draft):
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

        return {
            'creator_url': self.creator_url,
            'filled': filled,
            'message': '浏览器已打开并保持登录态。请在 B 站页面确认上传、保存草稿或发布；如果页面结构变化，可能需要手动补充。',
            'draft': {
                'title': draft['title'],
                'body': draft['body'],
                'tags': draft.get('tags', []),
                'cover_image': draft.get('cover_image', ''),
                'video_path': draft.get('video_path', ''),
            },
        }

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
