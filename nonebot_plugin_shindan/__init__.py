from nonebot.rule import Rule
from nonebot import on_command
from nonebot.typing import T_State
from nonebot.handler import Handler
from nonebot.adapters.cqhttp import Bot, Event, GroupMessageEvent

from .shindanmaker import get_shindan_title, NetworkError, ParseError, BrowserError
from .shindan_list import get_id, add_shindan, del_shindan, get_shindan_list, get_shindan_list_all


add_usage = """Usage:
添加占卜 {id} {指令}
如：添加占卜 917962 人设生成
"""

del_usage = """Usage:
删除占卜 {id}
如：删除占卜 917962
"""


def init_matchers():

    cmd_add = on_command('添加占卜', priority=8)
    cmd_del = on_command('删除占卜', priority=8)
    cmd_ls = on_command('占卜列表', priority=8)

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

        user_id = get_id(event)
        user_list = get_shindan_list(user_id)
        if id in user_list:
            await cmd_add.finish('该占卜已存在')

        if add_shindan(user_id, id, command, title):
            await cmd_add.finish(f'成功添加占卜“{title}”，可通过“{command} 名字”使用')

    @cmd_del.handle()
    async def _(bot: Bot, event: Event, state: T_State):
        arg = event.get_plaintext().strip()
        if not arg:
            await cmd_del.finish(del_usage)

        if not arg.isdigit():
            await cmd_del.finish(add_usage)

        id = arg
        user_id = get_id(event)
        user_list = get_shindan_list(user_id)
        if id not in user_list:
            await cmd_del.finish('不存在该占卜')

        if del_shindan(user_id, id):
            await cmd_del.finish(f'成功删除该占卜')

    @cmd_ls.handle()
    async def _(bot: Bot, event: Event, state: T_State):
        user_id = get_id(event)
        user_list = get_shindan_list(user_id)

        if not user_list:
            await cmd_ls.finish('尚未添加任何占卜')

        await cmd_ls.finish(f'可用占卜：\n' + '\n'.join([f"{s['command']} ({id})" for id, s in user_list.items()]))


def clear_matchers():
    pass


def update_matchers():
    clear_matchers()
    init_matchers()

    def check_user_id(user_id: str) -> Rule:
        async def _user_id(bot: "Bot", event: "Event", state: T_State) -> bool:
            return get_id(event) == user_id
        return Rule(_user_id)

    async def handler(bot: Bot, event: Event, state: T_State):
        pass

    for user_id, user_list in get_shindan_list_all().items():
        for _, shindan in user_list.items():
            command = shindan['command']
            matcher = on_command(
                command,
                rule=check_user_id(user_id),
                priority=9
            )
            matcher.append_handler(Handler(handler))


def get_id(event: Event):
    if isinstance(event, GroupMessageEvent):
        return 'group_' + str(event.group_id)
    else:
        return 'private_' + str(event.get_user_id())


update_matchers()
