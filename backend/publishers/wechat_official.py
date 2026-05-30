import json
import urllib.parse
import urllib.request

from ..config import WECHAT_APP_ID, WECHAT_APP_SECRET, WECHAT_DEFAULT_THUMB_MEDIA_ID


class WechatOfficialPublisher:
    token_url = 'https://api.weixin.qq.com/cgi-bin/token'
    draft_add_url = 'https://api.weixin.qq.com/cgi-bin/draft/add'

    def validate_token(self):
        self._validate_token_config()
        access_token = self._get_access_token()
        return {
            'status': 'success',
            'message': '已成功获取 access_token，微信测试号配置有效。',
            'access_token_preview': f'{access_token[:8]}...{access_token[-6:]}',
        }

    def publish(self, draft):
        self._validate_config()
        access_token = self._get_access_token()
        result = self._add_draft(access_token, draft)
        media_id = result.get('media_id', '')
        return {
            'status': 'success',
            'mode': 'wechat_draft',
            'external_id': media_id,
            'publish_url': '',
            'message': f'公众号草稿创建成功，media_id: {media_id}',
            'response_payload': result,
        }

    def _validate_config(self):
        missing = []
        if not WECHAT_APP_ID:
            missing.append('WECHAT_APP_ID')
        if not WECHAT_APP_SECRET:
            missing.append('WECHAT_APP_SECRET')
        if not WECHAT_DEFAULT_THUMB_MEDIA_ID:
            missing.append('WECHAT_DEFAULT_THUMB_MEDIA_ID')
        if missing:
            raise ValueError(f'缺少微信公众号配置：{", ".join(missing)}')

    def _validate_token_config(self):
        missing = []
        if not WECHAT_APP_ID:
            missing.append('WECHAT_APP_ID')
        if not WECHAT_APP_SECRET:
            missing.append('WECHAT_APP_SECRET')
        if missing:
            raise ValueError(f'缺少微信测试号配置：{", ".join(missing)}')

    def _get_access_token(self):
        params = urllib.parse.urlencode({
            'grant_type': 'client_credential',
            'appid': WECHAT_APP_ID,
            'secret': WECHAT_APP_SECRET,
        })
        response = self._request_json(f'{self.token_url}?{params}')
        if response.get('errcode'):
            raise RuntimeError(self._format_wechat_error(response, '获取 access_token 失败'))
        access_token = response.get('access_token')
        if not access_token:
            raise RuntimeError('获取 access_token 失败：微信接口未返回 access_token')
        return access_token

    def _add_draft(self, access_token, draft):
        params = urllib.parse.urlencode({'access_token': access_token})
        payload = {
            'articles': [
                {
                    'title': draft['title'],
                    'author': '创作者',
                    'digest': draft.get('summary', '')[:120],
                    'content': self._to_wechat_html(draft.get('body', '')),
                    'thumb_media_id': WECHAT_DEFAULT_THUMB_MEDIA_ID,
                    'need_open_comment': 1,
                    'only_fans_can_comment': 0,
                }
            ]
        }
        response = self._request_json(f'{self.draft_add_url}?{params}', payload)
        if response.get('errcode'):
            raise RuntimeError(self._format_wechat_error(response, '创建公众号草稿失败'))
        if not response.get('media_id'):
            raise RuntimeError('创建公众号草稿失败：微信接口未返回 media_id')
        return response

    def _request_json(self, url, payload=None):
        data = None
        headers = {}
        if payload is not None:
            data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
            headers['Content-Type'] = 'application/json; charset=utf-8'
        request = urllib.request.Request(url, data=data, headers=headers, method='POST' if payload is not None else 'GET')
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode('utf-8'))

    def _to_wechat_html(self, body):
        paragraphs = [line.strip() for line in body.splitlines() if line.strip()]
        return ''.join(f'<p>{self._escape_html(paragraph)}</p>' for paragraph in paragraphs)

    def _escape_html(self, text):
        return (
            text.replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
        )

    def _format_wechat_error(self, response, fallback):
        return f"{fallback}：{response.get('errmsg', '未知错误')}（errcode: {response.get('errcode')}）"
