from nonebot.rule import Rule
from nonebot.typing import T_State
from nonebot.permission import SUPERUSER
from nonebot import on_command, on_message
from nonebot.adapters.cqhttp import Bot, Event, MessageEvent, MessageSegment

from .shindan_list import add_shindan, del_shindan, get_shindan_list
from .shindanmaker import make_shindan, get_shindan_title, NetworkError, ParseError, BrowserError


__usage__ = """shindanmaker趣味占卜
发送“占卜列表”查看可用占卜
发送“{占卜名} {名字}”使用占卜"""

add_usage = """Usage:
添加占卜 {id} {指令}
如：添加占卜 917962 人设生成"""

del_usage = """Usage:
删除占卜 {id}
如：删除占卜 917962"""

cmd_sd = on_command('占卜', aliases={'shindan'}, priority=8)
cmd_ls = on_command('占卜列表', aliases={'可用占卜'}, priority=8)
cmd_add = on_command('添加占卜', permission=SUPERUSER, priority=8)
cmd_del = on_command('删除占卜', permission=SUPERUSER, priority=8)


@cmd_sd.handle()
async def _(bot: Bot, event: Event, state: T_State):
    await cmd_sd.finish(__usage__)


@cmd_ls.handle()
async def _(bot: Bot, event: Event, state: T_State):
    sd_list = get_shindan_list()

    if not sd_list:
        await cmd_ls.finish('尚未添加任何占卜')

    await cmd_ls.finish(f'可用占卜：\n' + '\n'.join([f"{s['command']} ({id})" for id, s in sd_list.items()]))


@cmd_add.handle()
async def _(bot: Bot, event: Event, state: T_State):
    arg = event.get_plaintext().strip()
    if not arg:
        await cmd_add.finish(add_usage)

    args = arg.split()
    if len(args) != 2 or not args[0].isdigit():
        await cmd_add.finish(add_usage)

    id = args[0]
    command = args[1]
    title = await get_shindan_title(id)
    if not title:
        await cmd_add.finish('找不到该占卜，请检查id')

    sd_list = get_shindan_list()
    if id in sd_list:
        await cmd_add.finish('该占卜已存在')

    if add_shindan(id, command, title):
        await cmd_add.finish(f'成功添加占卜“{title}”，可通过“{command} 名字”使用')


@cmd_del.handle()
async def _(bot: Bot, event: Event, state: T_State):
    arg = event.get_plaintext().strip()
    if not arg:
        await cmd_del.finish(del_usage)

    if not arg.isdigit():
        await cmd_del.finish(add_usage)

    id = arg
    sd_list = get_shindan_list()
    if id not in sd_list:
        await cmd_del.finish('不存在该占卜')

    if del_shindan(id):
        await cmd_del.finish(f'成功删除该占卜')


def sd_handler() -> Rule:
    async def handle(bot: "Bot", event: "Event", state: T_State) -> bool:
        if not isinstance(event, MessageEvent):
            return False

        msg = event.get_plaintext().strip()
        sd_list = get_shindan_list()
        for id, s in sd_list.items():
            command = s['command']
            if msg.startswith(command):
                name = msg[len(command):].strip()
                if not name or len(name) > 20:
                    return False
                state['id'] = id
                state['name'] = name
                return True
        return False
    return Rule(handle)


sd_matcher = on_message(sd_handler(), priority=9)


@sd_matcher.handle()
async def _(bot: Bot, event: Event, state: T_State):
    id = state['id']
    name = state['name']
    try:
        img = await make_shindan(id, name)
        await sd_matcher.finish(MessageSegment.image(img))
    except (NetworkError, ParseError):
        await sd_matcher.finish('网络错误，请检查代理或稍后再试')
    except BrowserError:
        await sd_matcher.finish('图片生成错误，请检查设置或稍后再试')
