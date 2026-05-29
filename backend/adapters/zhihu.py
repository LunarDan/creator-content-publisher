from .base_adapter import BaseAdapter


class ZhihuAdapter(BaseAdapter):
    platform_key = 'zhihu'
    platform_name = '知乎'
    description = '适合理性分析、问题导向和结构化论证。'

    def transform(self, content):
        title = self._trim_title(content['title'], 60)
        body = f"## 核心观点\n\n{content.get('summary') or '以下内容围绕该主题展开。'}\n\n## 详细说明\n\n{content['body']}\n\n## 总结\n\n欢迎补充你的看法。"
        return {
            'platform': self.platform_key,
            'title': title,
            'summary': content.get('summary', ''),
            'body': body,
            'tags': self._base_tags(content, 5),
            'cover_image': content.get('cover_image', ''),
            'extra_config': {'layout': 'column', 'tone': 'analytical'},
            'validation_warnings': [],
        }
