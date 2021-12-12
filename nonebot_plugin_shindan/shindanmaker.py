import httpx
from lxml import etree

from .browser import get_new_page
from .config import httpx_proxy, browser_proxy


class ShindanError(Exception):
    pass


class NetworkError(ShindanError):
    pass


class ParseError(ShindanError):
    pass


class BrowserError(ShindanError):
    pass


def retry(func):
    async def wrapper(*args, **kwargs):
        for i in range(3):
            try:
                return await func(*args, **kwargs)
            except:
                continue
        raise NetworkError
    return wrapper


@retry
async def get(client: httpx.AsyncClient, url: str, **kwargs):
    return await client.get(url, **kwargs)


@retry
async def post(client: httpx.AsyncClient, url: str, **kwargs):
    return await client.post(url, **kwargs)


async def get_shindan_title(id: int) -> str:
    url = f'https://cn.shindanmaker.com/{id}'
    try:
        async with httpx.AsyncClient(proxies=httpx_proxy) as client:
            resp = await get(client, url)
            return parse_title(resp.text)
    except:
        return ''


async def make_shindan(id: str, name: str) -> bytes:
    url = f'https://cn.shindanmaker.com/{id}'
    async with httpx.AsyncClient(proxies=httpx_proxy) as client:
        resp = await get(client, url)
        token = parse_token(resp.text)
        payload = {
            '_token': token,
            'shindanName': name,
            'hiddenName': '无名的Z'
        }
        resp = await post(client, url, json=payload)
    result = parse_result(resp.text)
    image = await create_image(result, wait=2000 if 'chart.js' in result else 0)
    return image


def parse_title(content: str) -> str:
    try:
        dom = etree.HTML(content)
        return dom.xpath("//h1[@id='shindanTitle']/a/text()")[0]
    except:
        raise ParseError


def parse_token(content: str) -> str:
    try:
        dom = etree.HTML(content)
        return dom.xpath("//form[@id='shindanForm']/input/@value")[0]
    except:
        raise ParseError


def parse_result(content: str) -> str:
    try:
        dom = etree.HTML(content)
        app_css = dom.xpath("//link[@rel='stylesheet']")[0]
        result_js = dom.xpath("//script[contains(text(), 'saveResult')]")[0]
        app_js = dom.xpath("//script[contains(@src, 'app.js')]")[0]
        title = dom.xpath(
            "//div[contains(@class, 'shindanTitleDescBlock')]")[0]
        result = dom.xpath("//div[@id='shindanResultBlock']")[0]
        chart_js = dom.xpath("//script[contains(@src, 'chart.js')]")

        new_dom = etree.HTML(
            '<html><head></head><body><div id="main-container"></div></body></html>')
        head = new_dom.xpath("//head")[0]
        head.append(app_css)
        head.append(result_js)
        head.append(app_js)
        if chart_js:
            head.append(chart_js[0])
        container = new_dom.xpath("//body/div")[0]
        container.append(title)
        container.append(result)
        return etree.tostring(new_dom, encoding='utf-8', method='html').decode()
    except:
        raise ParseError


async def create_image(html: str, wait: int = 0) -> bytes:
    try:
        async with get_new_page(viewport={"width": 800, "height": 100}, proxy=browser_proxy) as page:
            await page.set_content(html, wait_until='networkidle')
            await page.wait_for_timeout(wait)
            img = await page.screenshot(full_page=True)
        return img
    except:
        raise BrowserError
