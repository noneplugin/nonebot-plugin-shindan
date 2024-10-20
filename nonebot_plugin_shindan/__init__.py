import re
import traceback
from typing import Optional

from nonebot import get_driver, require
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata, inherit_supported_adapters
from nonebot.rule import to_me
from nonebot.typing import T_Handler

require("nonebot_plugin_orm")
require("nonebot_plugin_alconna")
require("nonebot_plugin_uninfo")
require("nonebot_plugin_htmlrender")

from arclet.alconna import Field
from nonebot_plugin_alconna import (
    Alconna,
    AlconnaMatcher,
    Args,
    At,
    Image,
    UniMessage,
    on_alconna,
)
from nonebot_plugin_alconna.model import CompConfig
from nonebot_plugin_uninfo import QryItrface, Uninfo

from .config import Config
from .manager import shindan_manager
from .model import ShindanConfig
from .shindanmaker import (
    download_image,
    get_shindan_title,
    make_shindan,
    render_shindan_list,
)

__plugin_meta__ = PluginMetadata(
    name="趣味占卜",
    description="使用ShindanMaker网站的趣味占卜",
    usage="发送“占卜列表”查看可用占卜\n发送“{占卜名} {名字}”使用占卜",
    type="application",
    homepage="https://github.com/noneplugin/nonebot-plugin-shindan",
    config=Config,
    supported_adapters=inherit_supported_adapters(
        "nonebot_plugin_alconna", "nonebot_plugin_uninfo"
    ),
)


params = {"use_cmd_start": True, "block": True, "priority": 13}

matcher_sd = on_alconna("占卜", rule=to_me(), **params)
matcher_ls = on_alconna("占卜列表", aliases={"可用占卜"}, **params)

comp_config = CompConfig(disables={"tab", "enter"}, timeout=60)
params_config = {"permission": SUPERUSER, "comp_config": comp_config, **params}

args_id = Args["id", int, Field(completion=lambda: "占卜id")]
args_cmd = Args["command", str, Field(completion=lambda: "占卜指令")]
args_mode = Args["mode", ["text", "image"], Field(completion=lambda: "占卜输出形式")]

matcher_add = on_alconna(
    Alconna("添加占卜", args_id, args_cmd),
    **params_config,
)
matcher_del = on_alconna(
    Alconna("删除占卜", args_id),
    **params_config,
)
matcher_set_cmd = on_alconna(
    Alconna("设置占卜指令", args_id, args_cmd),
    **params_config,
)
matcher_set_mode = on_alconna(
    Alconna("设置占卜模式", args_id, args_mode),
    **params_config,
)


@matcher_sd.handle()
async def _(matcher: Matcher):
    await matcher.finish(__plugin_meta__.usage)


@matcher_ls.handle()
async def _(matcher: Matcher):
    if not shindan_manager.shindan_list:
        await matcher.finish("尚未添加任何占卜")

    img = await render_shindan_list(shindan_manager.shindan_list)
    await UniMessage.image(raw=img).send()


@matcher_add.handle()
async def _(matcher: Matcher, id: int, command: str):
    for shindan in shindan_manager.shindan_list:
        if shindan.id == id:
            await matcher.finish("该占卜已存在")
        if shindan.command == command:
            await matcher.finish("该指令已被使用")

    title = await get_shindan_title(id)
    if not title:
        await matcher.finish("找不到该占卜，请检查id")

    await shindan_manager.add_shindan(id, command, title)
    refresh_matchers()
    await matcher.finish(f"成功添加占卜“{title}”，可通过“{command} 名字”使用")


@matcher_del.handle()
async def _(matcher: Matcher, id: int):
    if id not in (shindan.id for shindan in shindan_manager.shindan_list):
        await matcher.finish("尚未添加该占卜")

    await shindan_manager.remove_shindan(id)
    refresh_matchers()
    await matcher.finish("成功删除该占卜")


@matcher_set_cmd.handle()
async def _(matcher: Matcher, id: int, command: str):
    if id not in (shindan.id for shindan in shindan_manager.shindan_list):
        await matcher.finish("尚未添加该占卜")

    await shindan_manager.set_shindan(id, command=command)
    refresh_matchers()
    await matcher.finish("设置成功")


@matcher_set_mode.handle()
async def _(matcher: Matcher, id: int, mode: str):
    if id not in (shindan.id for shindan in shindan_manager.shindan_list):
        await matcher.finish("尚未添加该占卜")

    await shindan_manager.set_shindan(id, mode=mode)
    refresh_matchers()
    await matcher.finish("设置成功")


def shindan_handler(shindan: ShindanConfig) -> T_Handler:
    async def handler(
        matcher: Matcher,
        uninfo: Uninfo,
        interface: QryItrface,
        name: Optional[str] = None,
        at: Optional[At] = None,
    ):
        if at and (user := await interface.get_user(at.target)):
            name = user.nick or user.name

        if not name:
            user = uninfo.user
            name = user.nick or user.name

        if not name:
            await matcher.finish("无法获取名字，请加上名字再试")

        try:
            res = await make_shindan(shindan.id, name, shindan.mode)
        except Exception:
            logger.warning(traceback.format_exc())
            await matcher.finish("出错了，请稍后再试")

        msg = UniMessage()
        if isinstance(res, str):
            img_pattern = r"((?:http|https)://\S+\.(?:jpg|jpeg|png|gif|bmp|webp))"
            for text in re.split(img_pattern, res):
                if re.match(img_pattern, text):
                    try:
                        img = await download_image(text)
                        msg += Image(raw=img)
                    except Exception:
                        logger.warning(f"{text} 下载出错！")
                else:
                    msg += text
        else:
            msg += Image(raw=res)
        await msg.send()

    return handler


shindan_matchers: list[type[AlconnaMatcher]] = []


def refresh_matchers():
    for matcher in shindan_matchers:
        matcher.destroy()
    shindan_matchers.clear()

    for shindan in shindan_manager.shindan_list:
        matcher = on_alconna(
            Alconna(shindan.command, Args["name?", str]["at?", At]),
            block=True,
            priority=14,
        )
        matcher.append_handler(shindan_handler(shindan))
        shindan_matchers.append(matcher)


driver = get_driver()


@driver.on_startup
async def _():
    await shindan_manager.load_shindan()
    refresh_matchers()
