import httpx
import jinja2
import pkgutil
from lxml import etree
from typing import Tuple

from nonebot_plugin_htmlrender import html_to_pic


def retry(func):
    async def wrapper(*args, **kwargs):
        for i in range(3):
            try:
                return await func(*args, **kwargs)
            except:
                continue
        raise Exception('网络错误')
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
    url = f'https://shindanmaker.com/{id}'
    try:
        async with httpx.AsyncClient() as client:
            resp = await get(client, url)
            return parse_title(resp.text)
    except:
        return ''


async def make_shindan(id: str, name: str) -> bytes:
    url = f'https://shindanmaker.com/{id}'
    async with httpx.AsyncClient() as client:
        resp = await get(client, url)
        token = parse_token(resp.text)
        payload = {
            '_token': token,
            'shindanName': name,
            'hiddenName': '名無しのR'
        }
        resp = await post(client, url, json=payload)
    html, has_chart = await render_html(resp.text)
    return await html_to_pic(html, wait=2000 if has_chart else 0,
                             viewport={"width": 800, "height": 100})


def parse_title(content: str) -> str:
    try:
        dom = etree.HTML(content)
        return dom.xpath("//h1[@id='shindanTitle']/a/text()")[0]
    except:
        raise Exception('网站解析错误')


def parse_token(content: str) -> str:
    try:
        dom = etree.HTML(content)
        return dom.xpath("//form[@id='shindanForm']/input/@value")[0]
    except:
        raise Exception('网站解析错误')


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
    except:
        raise Exception('网站解析错误')

    html = await shindan_tpl.render_async(app_css=app_css,
                                          result_js=to_string(result_js),
                                          app_js=app_js,
                                          chart_js=chart_js if has_chart else '',
                                          title=to_string(title),
                                          result=to_string(result))
    return html, has_chart
