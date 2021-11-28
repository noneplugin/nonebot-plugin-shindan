from nonebot import get_driver


proxies = None
global_config = get_driver().config
proxy = global_config.http_proxy
if proxy:
    proxies = {
        'http': proxy,
        'https': proxy
    }
