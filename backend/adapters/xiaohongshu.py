from .base_adapter import BaseAdapter


class XiaohongshuAdapter(BaseAdapter):
    platform_key = 'xiaohongshu'
    platform_name = '小红书'
    description = '适合短标题、种草文案、分段和话题标签。'

    def transform(self, content):
        title = self._trim_title(content['title'], 20)
        tags = self._base_tags(content, 10)
        tag_line = ' '.join('#' + tag for tag in tags)
        body = f"{content.get('summary') or '今天分享一个实用内容'}\n\n{content['body']}\n\n{tag_line}"
        warnings = []
        if len(content['title']) > 20:
            warnings.append('小红书标题已自动压缩到 20 字以内。')
        return {
            'platform': self.platform_key,
            'title': title,
            'summary': content.get('summary', ''),
            'body': body,
            'tags': tags,
            'cover_image': content.get('cover_image', ''),
            'extra_config': {
                'layout': 'note',
                'tone': 'friendly',
                'video_path': content.get('video_path', ''),
                'thumbnail_path': content.get('cover_image', ''),
                'content_declaration': '',
                'original_declaration': '',
            },
            'validation_warnings': warnings,
        }
