from ..adapters.registry import get_adapter
from ..config import WECHAT_APP_ID, WECHAT_APP_SECRET, WECHAT_DEFAULT_THUMB_MEDIA_ID
from ..repositories.content_repository import ContentRepository
from ..repositories.platform_draft_repository import PlatformDraftRepository
from ..repositories.publish_task_repository import PublishTaskRepository


class ContentService:
    def __init__(self):
        self.contents = ContentRepository()
        self.drafts = PlatformDraftRepository()
        self.tasks = PublishTaskRepository()

    def list_contents(self):
        return self.contents.list()

    def get_content(self, content_id):
        return self.contents.get(content_id)

    def create_content(self, data):
        return self.contents.create(data)

    def update_content(self, content_id, data):
        return self.contents.update(content_id, data)

    def delete_content(self, content_id):
        return self.contents.delete(content_id)

    def adapt_content(self, content_id, platforms):
        content = self.contents.get(content_id)
        if not content:
            return None
        if not platforms:
            platforms = ['wechat_official', 'zhihu', 'bilibili', 'xiaohongshu', 'douyin', 'kuaishou']
        drafts = []
        for platform_key in platforms:
            adapter = get_adapter(platform_key)
            if not adapter:
                continue
            draft = adapter.transform(content)
            draft['content_id'] = content_id
            drafts.append(self.drafts.upsert(content_id, draft))
        return drafts

    def list_platform_drafts(self, content_id):
        return self.drafts.list_by_content(content_id)

    def update_platform_draft(self, draft_id, data):
        return self.drafts.update(draft_id, data)

    def simulate_publish(self, draft_id):
        draft = self.drafts.get(draft_id)
        if not draft:
            return None
        return self.tasks.create_simulated(draft)

    def simulate_publish_batch(self, draft_ids):
        results = []
        for draft_id in draft_ids:
            task = self.simulate_publish(draft_id)
            if task:
                results.append(task)
            else:
                results.append({
                    'platform_draft_id': draft_id,
                    'status': 'failed',
                    'error_message': '平台草稿不存在',
                })
        return results

    def publish_bilibili_with_browser(self, draft_id, auto_publish=True):
        draft = self.drafts.get(draft_id)
        if not draft:
            return None, '平台草稿不存在'
        if draft['platform'] != 'bilibili':
            return None, '仅支持 B站草稿浏览器发布'

        task = self.tasks.create_browser(draft)
        self.tasks.mark_running(task['id'])
        content = self.contents.get(draft['content_id']) or {}
        extra_config = draft.get('extra_config', {})
        draft = {
            **draft,
            'video_path': extra_config.get('video_path') or content.get('video_path', ''),
            'creation_declaration': extra_config.get('creation_declaration', 'no_label'),
        }
        try:
            from ..publishers.bilibili_browser import BilibiliBrowserPublisher
            result = BilibiliBrowserPublisher().publish(draft, auto_publish=auto_publish)
        except ModuleNotFoundError as exc:
            task = self.tasks.mark_failed(task['id'], '缺少 Playwright 依赖，请先安装后端依赖并执行 python -m playwright install chromium')
            return {'task': task}, '缺少 Playwright 依赖'
        except Exception as exc:
            task = self.tasks.mark_failed(task['id'], str(exc))
            return {'task': task}, 'B站浏览器发布启动失败'

        if result.get('status') in ('published', 'draft_saved'):
            task = self.tasks.mark_success(task['id'], result.get('publish_url', ''))
        else:
            task = self.tasks.mark_manual_pending(task['id'], result['message'])
        return {'task': task, 'result': result}, None

    def publish_douyin_with_browser(self, draft_id, auto_publish=True):
        draft = self.drafts.get(draft_id)
        if not draft:
            return None, '平台草稿不存在'
        if draft['platform'] != 'douyin':
            return None, '仅支持抖音草稿浏览器发布'

        task = self.tasks.create_browser(draft)
        self.tasks.mark_running(task['id'])
        content = self.contents.get(draft['content_id']) or {}
        extra_config = draft.get('extra_config', {})
        draft = {
            **draft,
            'video_path': extra_config.get('video_path') or content.get('video_path', ''),
        }
        try:
            from ..publishers.douyin_browser import DouyinBrowserPublisher
            result = DouyinBrowserPublisher().publish(draft, auto_publish=auto_publish)
        except ModuleNotFoundError:
            task = self.tasks.mark_failed(task['id'], '缺少 Playwright 依赖，请先安装后端依赖并执行 python -m playwright install chromium')
            return {'task': task}, '缺少 Playwright 依赖'
        except Exception as exc:
            task = self.tasks.mark_failed(task['id'], str(exc))
            return {'task': task}, '抖音浏览器发布启动失败'

        if result.get('status') in ('published', 'draft_saved'):
            task = self.tasks.mark_success(task['id'], result.get('publish_url', ''))
        else:
            task = self.tasks.mark_manual_pending(task['id'], result['message'])
        return {'task': task, 'result': result}, None

    def publish_kuaishou_with_browser(self, draft_id, auto_publish=False):
        draft = self.drafts.get(draft_id)
        if not draft:
            return None, '平台草稿不存在'
        if draft['platform'] != 'kuaishou':
            return None, '仅支持快手草稿浏览器发布'

        task = self.tasks.create_browser(draft)
        self.tasks.mark_running(task['id'])
        content = self.contents.get(draft['content_id']) or {}
        extra_config = draft.get('extra_config', {})
        draft = {
            **draft,
            'video_path': extra_config.get('video_path') or content.get('video_path', ''),
            'thumbnail_path': extra_config.get('thumbnail_path') or draft.get('cover_image', '') or content.get('cover_image', ''),
            'author_declaration': extra_config.get('author_declaration', ''),
        }
        try:
            from ..publishers.kuaishou_browser import KuaishouBrowserPublisher
            result = KuaishouBrowserPublisher().publish(draft, auto_publish=False)
        except ModuleNotFoundError as exc:
            task = self.tasks.mark_failed(task['id'], '缺少 Playwright 依赖，请先安装后端依赖并执行 python -m playwright install chromium')
            return {'task': task}, '缺少 Playwright 依赖'
        except Exception as exc:
            message = self._format_kuaishou_browser_error(exc)
            task = self.tasks.mark_manual_pending(task['id'], message)
            return {'task': task, 'result': {'status': 'manual_pending', 'message': message, 'draft': self._kuaishou_browser_draft_payload(draft), 'filled': []}}, None

        task = self.tasks.mark_manual_pending(task['id'], result.get('message', '请在快手页面人工完成发布'))
        return {'task': task, 'result': result}, None

    def publish_zhihu_with_browser(self, draft_id, auto_publish=False):
        draft = self.drafts.get(draft_id)
        if not draft:
            return None, '平台草稿不存在'
        if draft['platform'] != 'zhihu':
            return None, '仅支持知乎草稿浏览器发布'

        task = self.tasks.create_browser(draft)
        self.tasks.mark_running(task['id'])
        content = self.contents.get(draft['content_id']) or {}
        extra_config = draft.get('extra_config', {})
        draft = {
            **draft,
            'cover_image': extra_config.get('zhihu_cover_image') or draft.get('cover_image', '') or content.get('cover_image', ''),
            'creation_declaration': extra_config.get('zhihu_creation_declaration', 'no_label'),
        }
        try:
            from ..publishers.zhihu_browser import ZhihuBrowserPublisher
            result = ZhihuBrowserPublisher().publish(draft, auto_publish=False)
        except ModuleNotFoundError:
            task = self.tasks.mark_failed(task['id'], '缺少 Playwright 依赖，请先安装后端依赖并执行 python -m playwright install chromium')
            return {'task': task}, '缺少 Playwright 依赖'
        except Exception as exc:
            message = self._format_zhihu_browser_error(exc)
            task = self.tasks.mark_manual_pending(task['id'], message)
            return {'task': task, 'result': {'status': 'manual_pending', 'message': message, 'draft': self._browser_draft_payload(draft)}}, None

        task = self.tasks.mark_manual_pending(task['id'], result.get('message', '请在知乎页面人工完成发布'))
        return {'task': task, 'result': result}, None

    def _format_zhihu_browser_error(self, exc):
        error_text = str(exc)
        if '40362' in error_text or '请求存在异常' in error_text or 'temporarily restricted' in error_text:
            return '知乎平台限制了本次访问，请在打开的知乎页面人工处理，不要连续自动重试。'
        if 'Target page, context or browser has been closed' in error_text:
            return '知乎浏览器窗口已关闭或已有会话占用，请关闭已打开的知乎自动化窗口后再使用发布助手。'
        return '知乎发布助手启动后未能自动完成，请在知乎页面人工处理。'

    def _browser_draft_payload(self, draft):
        return {
            'platform': draft.get('platform', ''),
            'title': draft.get('title', ''),
            'body': draft.get('body', ''),
            'tags': draft.get('tags', []),
            'cover_image': draft.get('cover_image', ''),
            'creation_declaration': draft.get('creation_declaration', ''),
        }

    def _format_kuaishou_browser_error(self, exc):
        error_text = str(exc)
        if 'Target page, context or browser has been closed' in error_text:
            return '快手浏览器窗口已关闭或已有会话占用，请关闭已打开的快手自动化窗口后再使用发布助手。'
        return '快手发布助手启动后未能自动完成，请在快手页面人工处理。'

    def _kuaishou_browser_draft_payload(self, draft):
        return {
            'title': draft.get('title', ''),
            'body': draft.get('body', ''),
            'tags': draft.get('tags', []),
            'video_path': draft.get('video_path', ''),
            'thumbnail_path': draft.get('thumbnail_path', ''),
            'author_declaration': draft.get('author_declaration', ''),
        }

    def publish_wechat_draft(self, draft_id):
        draft = self.drafts.get(draft_id)
        if not draft:
            return None, '平台草稿不存在'
        if draft['platform'] != 'wechat_official':
            return None, '仅支持公众号草稿发布'

        task = self.tasks.create_wechat_draft(draft)
        self.tasks.mark_running(task['id'])
        try:
            from ..publishers.registry import get_publisher
            publisher = get_publisher('wechat_draft')
            result = publisher.publish(draft)
        except ValueError as exc:
            task = self.tasks.mark_failed(task['id'], str(exc))
            return {'task': task}, str(exc)
        except Exception as exc:
            task = self.tasks.mark_failed(task['id'], str(exc))
            return {'task': task}, '公众号草稿发布失败'

        task = self.tasks.mark_success(
            task['id'],
            result.get('publish_url', ''),
            result.get('external_id', ''),
            result.get('response_payload', {}),
        )
        return {'task': task, 'result': result}, None

    def get_wechat_publish_config(self):
        return {
            'app_id_configured': bool(WECHAT_APP_ID),
            'app_secret_configured': bool(WECHAT_APP_SECRET),
            'thumb_media_id_configured': bool(WECHAT_DEFAULT_THUMB_MEDIA_ID),
        }

    def check_wechat_token(self):
        try:
            from ..publishers.registry import get_publisher
            publisher = get_publisher('wechat_draft')
            return publisher.validate_token(), None
        except ValueError as exc:
            return None, str(exc)
        except Exception as exc:
            return None, str(exc)

    def complete_manual_publish(self, task_id, publish_url):
        task = self.tasks.get(task_id)
        if not task:
            return None, '发布任务不存在'
        if task['mode'] not in ('browser', 'manual'):
            return None, '只能完成浏览器或手动发布任务'
        return self.tasks.mark_success(task_id, publish_url), None
