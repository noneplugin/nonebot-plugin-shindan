import re
import time
from pathlib import Path
from typing import List, Tuple, Union

import httpx
import jinja2
from bs4 import BeautifulSoup, Tag
from nonebot_plugin_htmlrender import html_to_pic

from .config import shindan_config
from .model import ShindanConfig

tpl_path = Path(__file__).parent / "templates"
env = jinja2.Environment(loader=jinja2.FileSystemLoader(tpl_path), enable_async=True)


headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/96.0.4664.110 Safari/537.36"
    )
}

if shindan_config.shindanmaker_cookie:
    headers["cookie"] = shindan_config.shindanmaker_cookie


async def request(client: httpx.AsyncClient, method: str, url: str, **kwargs):
    resp = await client.request(
        method, url, headers=headers, timeout=20, follow_redirects=True, **kwargs
    )
    resp.raise_for_status()
    return resp


async def get(client: httpx.AsyncClient, url: str, **kwargs):
    return await request(client, "GET", url, **kwargs)


async def post(client: httpx.AsyncClient, url: str, **kwargs):
    return await request(client, "POST", url, **kwargs)


async def download_image(url: str) -> bytes:
    async with httpx.AsyncClient() as client:
        resp = await get(client, url)
        return resp.read()


async def get_shindan_title(id: int) -> str:
    url = f"https://shindanmaker.com/{id}"
    async with httpx.AsyncClient() as client:
        resp = await get(client, url)
        dom = BeautifulSoup(resp.text, "lxml")
        title = dom.find("h1", {"id": "shindanTitle"})
        assert title
        return title.text


async def make_shindan(id: int, name: str, mode="image") -> Union[str, bytes]:
    url = f"https://shindanmaker.com/{id}"
    seed = time.strftime("%y%m%d", time.localtime())
    async with httpx.AsyncClient() as client:
        resp = await get(client, url)
        dom = BeautifulSoup(resp.text, "lxml")
        form = dom.find("form", {"id": "shindanForm"})
        _token = form.find("input", {"name": "_token"})["value"]  # type: ignore
        shindan_token = form.find("input", {"name": "shindan_token"})["value"]  # type: ignore
        payload = {
            "_token": _token,
            "shindanName": name + seed,
            "hiddenName": "名無しのR",
            "type": "name",
            "shindan_token": shindan_token,
        }
        resp = await post(client, url, json=payload)

    content = resp.text
    if mode == "image":
        html, has_chart = await render_html(content)
        html = html.replace(seed, "")
        return await html_to_pic(
            html,
            template_path=f"file://{tpl_path.absolute()}",
            wait=2000 if has_chart else 0,
            viewport={"width": 750, "height": 100},
        )
    else:
        dom = BeautifulSoup(content, "lxml")
        result = dom.find("span", {"id": "shindanResult"})
        assert isinstance(result, Tag)
        for img in result.find_all("img"):
            img.replace_with(img["src"])
        return result.text.replace(seed, "")


def remove_shindan_effects(content: Tag, type: str):
    for tag in content.find_all("span", {"class": "shindanEffects", "data-mode": type}):
        assert isinstance(tag, Tag)
        if noscript := tag.find_next("noscript"):
            noscript.replace_with_children()
            tag.extract()


async def render_html(content: str) -> Tuple[str, bool]:
    dom = BeautifulSoup(content, "lxml")
    result_js = str(dom.find("script", string=re.compile(r"savedShindanResult")))
    title = str(dom.find("h1", {"id": "shindanResultAbove"}))
    result = dom.find("div", {"id": "shindanResultBlock"})
    assert isinstance(result, Tag)
    remove_shindan_effects(result, "ef_shuffle")
    remove_shindan_effects(result, "ef_typing")
    result = str(result)
    has_chart = "chart.js" in content

    shindan_tpl = env.get_template("shindan.html")
    html = await shindan_tpl.render_async(
        result_js=result_js, title=title, result=result, has_chart=has_chart
    )
    return html, has_chart


async def render_shindan_list(shindan_list: List[ShindanConfig]) -> bytes:
    tpl = env.get_template("shindan_list.html")
    html = await tpl.render_async(shindan_list=shindan_list)
    return await html_to_pic(
        html,
        template_path=f"file://{tpl_path.absolute()}",
        viewport={"width": 100, "height": 100},
    )
