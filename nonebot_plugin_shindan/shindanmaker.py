import httpx
import jinja2
import pkgutil
from lxml import etree
from typing import Tuple

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


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
}


@retry
async def get(client: httpx.AsyncClient, url: str, **kwargs):
    return await client.get(url, headers=headers, timeout=10, **kwargs)


@retry
async def post(client: httpx.AsyncClient, url: str, **kwargs):
    return await client.post(url, headers=headers, timeout=10, **kwargs)


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
    html, has_chart = await render_html(resp.text)
    image = await create_image(html, wait=2000 if has_chart else 0)
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


def load_file(name: str) -> str:
    return pkgutil.get_data(__name__, f"templates/{name}").decode()


env = jinja2.Environment(enable_async=True)
shindan_tpl = env.from_string(load_file('shindan.html'))
app_css = load_file('app.css')
app_js = load_file('app.js')
chart_js = load_file('chart.js')


def to_string(dom) -> str:
    return etree.tostring(dom, encoding='utf-8', method='html').decode()


async def render_html(content: str) -> Tuple[str, bool]:
    try:
        dom = etree.HTML(content)
        result_js = dom.xpath("//script[contains(text(), 'saveResult')]")[0]
        title = dom.xpath(
            "//div[contains(@class, 'shindanTitleDescBlock')]")[0]
        result = dom.xpath("//div[@id='shindanResultBlock']")[0]
        has_chart = dom.xpath("//script[contains(@src, 'chart.js')]")
        html = await shindan_tpl.render_async(app_css=app_css,
                                              result_js=to_string(result_js),
                                              app_js=app_js,
                                              chart_js=chart_js if has_chart else '',
                                              title=to_string(title),
                                              result=to_string(result))
        return html, has_chart
    except:
        raise ParseError


async def create_image(html: str, wait: int = 0) -> bytes:
    try:
        async with get_new_page(viewport={"width": 800, "height": 100}, proxy=browser_proxy) as page:
            await page.set_content(html)
            await page.wait_for_timeout(wait)
            img = await page.screenshot(full_page=True)
        return img
    except:
        raise BrowserError
