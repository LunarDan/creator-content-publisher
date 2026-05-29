class BaseAdapter:
    platform_key = ''
    platform_name = ''
    description = ''

    def transform(self, content):
        raise NotImplementedError

    def _base_tags(self, content, limit=6):
        return (content.get('tags') or [])[:limit]

    def _trim_title(self, title, limit):
        title = (title or '').strip()
        return title if len(title) <= limit else title[:limit - 1] + '…'
