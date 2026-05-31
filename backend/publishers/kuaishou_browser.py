from pathlib import Path

from playwright.sync_api import Error as PlaywrightError, sync_playwright


_sessions = []
DATA_DIR = Path(__file__).resolve().parents[1] / 'data' / 'browser'
KUAISHOU_USER_DATA_DIR = DATA_DIR / 'kuaishou'


class KuaishouBrowserPublisher:
    creator_url = 'https://cp.kuaishou.com/article/publish/video'

    def publish(self, draft, auto_publish=False):
        context, page = self._open_browser_context()
        filled = []
        page.goto(self.creator_url, wait_until='domcontentloaded')
        page.wait_for_timeout(3000)
        if draft.get('video_path'):
            self._try_upload_video(page, draft['video_path'], filled)
            self._wait_until_upload_ready(page)
        self._dismiss_guides(page)
        self._fill_description_and_tags(page, draft, filled)
        self._try_apply_cover(page, draft.get('thumbnail_path') or draft.get('cover_image') or '', filled)
        self._try_select_author_declaration(page, draft.get('author_declaration') or '', filled)

        return {
            'creator_url': self.creator_url,
            'status': 'manual_pending',
            'filled': filled,
            'message': '浏览器已打开快手创作页并尽力填充内容。请在快手页面人工检查、保存草稿或发布；系统不会自动点击最终发布按钮。',
            'draft': {
                'title': draft.get('title', ''),
                'body': draft.get('body', ''),
                'tags': draft.get('tags', []),
                'video_path': draft.get('video_path', ''),
                'thumbnail_path': draft.get('thumbnail_path', ''),
                'author_declaration': draft.get('author_declaration', ''),
            },
        }

    def _open_browser_context(self):
        self._cleanup_closed_sessions()
        try:
            return self._launch_browser_context()
        except PlaywrightError:
            self._close_all_sessions()
            return self._launch_browser_context()

    def _launch_browser_context(self):
        KUAISHOU_USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
        playwright = sync_playwright().start()
        try:
            context = playwright.chromium.launch_persistent_context(
                user_data_dir=str(KUAISHOU_USER_DATA_DIR),
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

        for selector in ['button[class^="_upload-btn"]', 'button:has-text("上传")', '[role="button"]:has-text("上传")']:
            try:
                button = page.locator(selector).first
                button.wait_for(state='visible', timeout=5000)
                with page.expect_file_chooser(timeout=10000) as chooser_info:
                    button.click(timeout=5000)
                chooser_info.value.set_files(str(path))
                filled.append('视频文件')
                return True
            except Exception:
                continue

        try:
            file_input = page.locator('input[type="file"]').first
            file_input.wait_for(state='attached', timeout=5000)
            file_input.set_input_files(str(path))
            filled.append('视频文件')
            return True
        except Exception:
            return False

    def _wait_until_upload_ready(self, page):
        for _ in range(60):
            if self._visible_text(page, '上传失败'):
                return False
            if not self._visible_text(page, '上传中'):
                return True
            page.wait_for_timeout(2000)
        return False

    def _dismiss_guides(self, page):
        self._click_text(page, '我知道了')
        for selector in [
            'div[role="alertdialog"] [data-action="skip"]',
            'div[role="alertdialog"] [aria-label="Skip"]',
            'div[id^="react-joyride-step"] [data-action="skip"]',
            'div[id^="react-joyride-step"] [aria-label="Skip"]',
        ]:
            try:
                page.locator(selector).first.click(timeout=2000, force=True)
                page.wait_for_timeout(500)
            except Exception:
                continue

    def _fill_description_and_tags(self, page, draft, filled):
        value = (draft.get('body') or draft.get('title') or '').strip()
        if not value:
            return False

        for locator in [
            page.locator('text=描述').locator('xpath=following-sibling::div').first,
            page.locator('textarea').first,
            page.locator('[contenteditable="true"]').first,
        ]:
            try:
                locator.wait_for(state='visible', timeout=5000)
                locator.click(timeout=5000)
                page.keyboard.press('Control+A')
                page.keyboard.press('Backspace')
                page.keyboard.type(value, delay=10)
                page.keyboard.press('Enter')
                filled.append('描述')
                break
            except Exception:
                continue

        for tag in (draft.get('tags') or [])[:3]:
            try:
                page.keyboard.type(f'#{tag} ', delay=10)
                page.wait_for_timeout(500)
                filled.append(f'#{tag}')
            except Exception:
                continue
        return True

    def _try_apply_cover(self, page, cover_image, filled):
        cover_image = (cover_image or '').strip()
        if not cover_image:
            return False
        cover_path = Path(cover_image).expanduser()
        if not cover_path.exists() or not cover_path.is_file():
            return False

        try:
            cover_area = page.locator("div[class*='default-cover']").first
            cover_area.hover(timeout=3000)
            page.wait_for_timeout(800)
            page.locator("div[class*='cover-full-editor']").first.click(timeout=5000)
        except Exception:
            for selector in ['button:has-text("封面")', '[role="button"]:has-text("封面")', 'button:has-text("上传封面")']:
                try:
                    page.locator(selector).first.click(timeout=3000)
                    break
                except Exception:
                    continue

        modal = page.locator('div[role="document"].ant-modal:visible').first
        try:
            modal.wait_for(state='visible', timeout=5000)
            try:
                modal.locator("div[class*='header-title-item']").nth(1).click(timeout=3000)
                page.wait_for_timeout(800)
            except Exception:
                pass
            modal.locator("input[type='file']").first.set_input_files(str(cover_path))
            page.wait_for_timeout(1500)
            self._click_text(page, '确认')
            filled.append('封面')
            return True
        except Exception:
            return False

    def _try_select_author_declaration(self, page, value, filled):
        value = (value or '').strip()
        if not value:
            return False
        candidates = self._resolve_author_declaration(value)

        opened = False
        for placeholder in ['为作品添加补充说明', '补充说明', '请选择', '作者声明', '声明']:
            try:
                input_el = page.locator(f"input[placeholder*='{placeholder}']").first
                input_el.wait_for(state='visible', timeout=2000)
                wrapper = input_el.locator("xpath=ancestor::div[contains(@class, 'ant-select')]").first
                wrapper.click(timeout=3000)
                opened = True
                break
            except Exception:
                continue
        if not opened:
            for text in ['作者声明', '补充说明', '声明']:
                if self._click_text(page, text):
                    opened = True
                    break
        if not opened:
            return False

        page.wait_for_timeout(500)
        for candidate in candidates:
            for selector in [
                f"div.ant-select-item-option:has-text('{candidate}')",
                f"[role='option']:has-text('{candidate}')",
                f"text={candidate}",
            ]:
                try:
                    page.locator(selector).first.click(timeout=3000)
                    filled.append('作者声明')
                    return True
                except Exception:
                    continue
        return False

    def _click_text(self, page, text):
        for selector in [f'text={text}', f'button:has-text("{text}")', f'[role="button"]:has-text("{text}")']:
            try:
                page.locator(selector).first.click(timeout=1500)
                return True
            except Exception:
                continue
        return False

    def _visible_text(self, page, text):
        try:
            return page.locator(f'text={text}').first.is_visible(timeout=800)
        except Exception:
            return False

    @staticmethod
    def _resolve_author_declaration(value):
        mapping = {
            'no_label': ['不声明', '无声明', '无需声明'],
            'none': ['不声明', '无声明', '无需声明'],
            'original': ['原创', '声明原创'],
            'repost': ['转载'],
            'authorized': ['授权转载', '授权'],
        }
        return mapping.get(value, [value])
