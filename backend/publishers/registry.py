from .bilibili_browser import BilibiliBrowserPublisher
from .wechat_official import WechatOfficialPublisher

PUBLISHERS = {
    'wechat_draft': WechatOfficialPublisher(),
}


def get_publisher(mode):
    return PUBLISHERS.get(mode)


def list_publish_modes():
    return list(PUBLISHERS.keys())
