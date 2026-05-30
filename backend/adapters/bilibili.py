from .base_adapter import BaseAdapter


class BilibiliAdapter(BaseAdapter):
    platform_key = 'bilibili'
    platform_name = 'B站'
    description = '适合视频简介、专栏和动态分发。'

    def transform(self, content):
        title = self._trim_title(content['title'], 80)
        tags = self._base_tags(content, 10)
        body = f"{content.get('summary') or content['title']}\n\n{content['body']}\n\n相关标签：{' '.join('#' + tag for tag in tags)}"
        warnings = []
        if len(tags) < 2:
            warnings.append('建议至少提供 2 个标签，便于 B站推荐。')
        return {
            'platform': self.platform_key,
            'title': title,
            'summary': content.get('summary', ''),
            'body': body,
            'tags': tags,
            'cover_image': content.get('cover_image', ''),
            'extra_config': {'layout': 'video_description', 'tone': 'community', 'video_path': content.get('video_path', '')},
            'validation_warnings': warnings,
        }
