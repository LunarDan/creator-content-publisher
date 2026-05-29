from .base_adapter import BaseAdapter


class WechatOfficialAdapter(BaseAdapter):
    platform_key = 'wechat_official'
    platform_name = '公众号'
    description = '适合长文排版、摘要和结构化表达。'

    def transform(self, content):
        title = self._trim_title(content['title'], 64)
        body = f"# {title}\n\n{content.get('summary', '')}\n\n---\n\n{content['body']}"
        warnings = []
        if not content.get('summary'):
            warnings.append('建议补充摘要，便于公众号图文分发。')
        return {
            'platform': self.platform_key,
            'title': title,
            'summary': content.get('summary', ''),
            'body': body,
            'tags': self._base_tags(content, 5),
            'cover_image': content.get('cover_image', ''),
            'extra_config': {'layout': 'article', 'tone': 'formal'},
            'validation_warnings': warnings,
        }
