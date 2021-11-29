from nonebot import get_driver


httpx_proxy = None
browser_proxy = None
global_config = get_driver().config
http_proxy = global_config.http_proxy

if http_proxy:
    httpx_proxy = {
        'http://': http_proxy,
        'https://': http_proxy
    }
    browser_proxy = {
        'server': http_proxy
    }
