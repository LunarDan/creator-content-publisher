export function platformName(platform) {
  const platformMap = {
    wechat_official: '公众号',
    zhihu: '知乎',
    bilibili: 'B站',
    xiaohongshu: '小红书',
  }

  return platformMap[platform] || platform
}
