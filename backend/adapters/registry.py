from .bilibili import BilibiliAdapter
from .douyin import DouyinAdapter
from .wechat_official import WechatOfficialAdapter
from .xiaohongshu import XiaohongshuAdapter
from .zhihu import ZhihuAdapter

ADAPTERS = {
    adapter.platform_key: adapter()
    for adapter in [WechatOfficialAdapter, ZhihuAdapter, BilibiliAdapter, XiaohongshuAdapter, DouyinAdapter]
}


def list_platforms():
    return [
        {
            'key': adapter.platform_key,
            'name': adapter.platform_name,
            'description': adapter.description,
        }
        for adapter in ADAPTERS.values()
    ]


def get_adapter(platform_key):
    return ADAPTERS.get(platform_key)
