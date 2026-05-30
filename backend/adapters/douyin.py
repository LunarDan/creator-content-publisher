from .base_adapter import BaseAdapter


class DouyinAdapter(BaseAdapter):
    platform_key = 'douyin'
    platform_name = '抖音'
    description = '适合短视频标题、简介和话题分发。'

    def transform(self, content):
        title = self._trim_title(content['title'], 30)
        tags = self._base_tags(content, 5)
        body = content.get('summary') or content['body'][:180]
        if tags:
            body = f"{body}\n\n{' '.join('#' + tag for tag in tags)}"
        warnings = []
        if not content.get('video_path'):
            warnings.append('抖音浏览器辅助发布建议填写本机视频文件路径。')
        if len(tags) < 2:
            warnings.append('建议至少提供 2 个话题标签，便于抖音分发。')
        return {
            'platform': self.platform_key,
            'title': title,
            'summary': content.get('summary', ''),
            'body': body,
            'tags': tags,
            'cover_image': content.get('cover_image', ''),
            'extra_config': {
                'layout': 'short_video_description',
                'tone': 'short_video',
                'video_path': content.get('video_path', ''),
                'manual_publish_required': True,
            },
            'validation_warnings': warnings,
        }
