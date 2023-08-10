import re
import traceback
from typing import List, Optional, Union

from nonebot import on_command, on_message, require
from nonebot.adapters import Bot, Event, Message
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, EventMessage, EventPlainText
from nonebot.permission import SUPERUSER
from nonebot.plugin import PluginMetadata
from nonebot.rule import Rule, to_me
from nonebot.typing import T_State

require("nonebot_plugin_datastore")
require("nonebot_plugin_htmlrender")
require("nonebot_plugin_saa")

from nonebot_plugin_datastore.db import post_db_init
from nonebot_plugin_saa import Image, MessageFactory
from nonebot_plugin_saa import __plugin_meta__ as saa_plugin_meta

from .config import Config
from .manager import shindan_manager
from .shindanmaker import (
    download_image,
    get_shindan_title,
    make_shindan,
    render_shindan_list,
)

post_db_init(shindan_manager.load_shindan_records)

__plugin_meta__ = PluginMetadata(
    name="趣味占卜",
    description="使用ShindanMaker网站的趣味占卜",
    usage="发送“占卜列表”查看可用占卜\n发送“{占卜名} {名字}”使用占卜",
    type="application",
    homepage="https://github.com/noneplugin/nonebot-plugin-shindan",
    config=Config,
    supported_adapters=saa_plugin_meta.supported_adapters,
    extra={
        "unique_name": "shindan",
        "example": "人设生成 小Q",
        "author": "meetwq <meetwq@gmail.com>",
        "version": "0.4.1",
    },
)

add_usage = """Usage:
添加占卜 {id} {指令}
如：添加占卜 917962 人设生成"""

del_usage = """Usage:
删除占卜 {id}
如：删除占卜 917962"""

set_usage = """Usage:
设置占卜 {id} {mode}
设置占卜输出模式：'text' 或 'image'(默认)
如：设置占卜 360578 text"""

cmd_sd = on_command(
    "占卜", aliases={"shindan", "shindanmaker"}, rule=to_me(), block=True, priority=13
)
cmd_ls = on_command("占卜列表", aliases={"可用占卜"}, block=True, priority=13)
cmd_add = on_command("添加占卜", permission=SUPERUSER, block=True, priority=13)
cmd_del = on_command("删除占卜", permission=SUPERUSER, block=True, priority=13)
cmd_set = on_command("设置占卜", permission=SUPERUSER, block=True, priority=13)


@cmd_sd.handle()
async def _():
    await cmd_sd.finish(__plugin_meta__.usage)


@cmd_ls.handle()
async def _(matcher: Matcher):
    if not shindan_manager.shindan_records:
        await matcher.finish("尚未添加任何占卜")

    img = await render_shindan_list(shindan_manager.shindan_records)
    await MessageFactory(Image(img)).send()
    await matcher.finish()


@cmd_add.handle()
async def _(matcher: Matcher, msg: Message = CommandArg()):
    arg = msg.extract_plain_text().strip()
    if not arg:
        await matcher.finish(add_usage)

    args = arg.split()
    if len(args) != 2 or not args[0].isdigit():
        await matcher.finish(add_usage)

    id = args[0]
    command = args[1]
    title = await get_shindan_title(id)
    if not title:
        await matcher.finish("找不到该占卜，请检查id")

    if resp := await shindan_manager.add_shindan(id, command, title):
        await matcher.finish(resp)
    else:
        await matcher.finish(f"成功添加占卜“{title}”，可通过“{command} 名字”使用")


@cmd_del.handle()
async def _(matcher: Matcher, msg: Message = CommandArg()):
    arg = msg.extract_plain_text().strip()
    if not arg:
        await matcher.finish(del_usage)

    if not arg.isdigit():
        await matcher.finish(del_usage)

    id = arg

    if resp := await shindan_manager.remove_shindan(id):
        await matcher.finish(resp)
    else:
        await matcher.finish("成功删除该占卜")


@cmd_set.handle()
async def _(matcher: Matcher, msg: Message = CommandArg()):
    arg = msg.extract_plain_text().strip()
    if not arg:
        await matcher.finish(set_usage)

    args = arg.split()
    if len(args) != 2 or not args[0].isdigit() or args[1] not in ["text", "image"]:
        await matcher.finish(set_usage)

    id = args[0]
    mode = args[1]

    if resp := await shindan_manager.set_shindan_mode(id, mode):
        await matcher.finish(resp)
    else:
        await matcher.finish("设置成功")


try:
    from .onebot import get_mention_username, get_sender_username
except ImportError:
    get_mention_username = None
    get_sender_username = None


def sd_handler() -> Rule:
    async def handle(
        bot: Bot,
        event: Event,
        state: T_State,
        msg: Message = EventMessage(),
        msg_text: str = EventPlainText(),
    ) -> bool:
        async def get_name(command: str) -> Optional[str]:
            name = None
            if get_mention_username:
                name = await get_mention_username(bot, event, msg)

            if not name:
                name = msg_text[len(command) :].strip()

            if not name and get_sender_username:
                name = await get_sender_username(bot, event)

            return name

        for record in sorted(
            shindan_manager.shindan_records,
            reverse=True,
            key=lambda record: record.command,
        ):
            if msg_text.startswith(record.command):
                name = await get_name(record.command)
                state["id"] = record.shindan_id
                state["name"] = name
                state["mode"] = record.mode
                return True
        return False

    return Rule(handle)


sd_matcher = on_message(sd_handler(), priority=13)


@sd_matcher.handle()
async def _(state: T_State, matcher: Matcher):
    id: str = state["id"]
    name: Optional[str] = state["name"]
    mode: str = state["mode"]

    if name is None:
        await matcher.finish("无法获取名字，请加上名字再试")

    try:
        res = await make_shindan(id, name, mode)
    except:
        logger.warning(traceback.format_exc())
        await matcher.finish("出错了，请稍后再试")

    msgs: List[Union[str, bytes]] = []
    if isinstance(res, str):
        img_pattern = r"((?:http|https)://\S+\.(?:jpg|jpeg|png|gif|bmp|webp))"
        for msg in re.split(img_pattern, res):
            if re.match(img_pattern, msg):
                try:
                    img = await download_image(msg)
                    msgs.append(img)
                except:
                    logger.warning(f"{msg} 下载出错！")
            else:
                msgs.append(msg)
    elif isinstance(res, bytes):
        msgs.append(res)

    if not msgs:
        await matcher.finish()

    msg_builder = MessageFactory([])
    for msg in msgs:
        if isinstance(msg, bytes):
            msg_builder.append(Image(msg))
        else:
            msg_builder.append(msg)
    await msg_builder.send()
    await matcher.finish()
