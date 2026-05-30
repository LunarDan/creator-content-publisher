from .base_adapter import BaseAdapter


class KuaishouAdapter(BaseAdapter):
    platform_key = 'kuaishou'
    platform_name = '快手'
    description = '适合短视频发布、话题标签和创作者中心分发。'

    def transform(self, content):
        title = self._trim_title(content['title'], 40)
        tags = self._base_tags(content, 6)
        body = content.get('summary') or content['body']
        warnings = []
        if not content.get('video_path'):
            warnings.append('快手真实发布需要在预览中心填写本机视频文件路径。')
        return {
            'platform': self.platform_key,
            'title': title,
            'summary': content.get('summary', ''),
            'body': body,
            'tags': tags,
            'cover_image': content.get('cover_image', ''),
            'extra_config': {
                'layout': 'short_video',
                'tone': 'creator',
                'video_path': content.get('video_path', ''),
                'thumbnail_path': content.get('cover_image', ''),
                'author_declaration': '',
            },
            'validation_warnings': warnings,
        }
