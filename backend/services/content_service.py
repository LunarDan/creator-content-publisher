from ..adapters.registry import get_adapter
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
            platforms = ['wechat_official', 'zhihu', 'bilibili', 'xiaohongshu']
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
