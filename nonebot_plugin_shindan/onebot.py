from typing import Optional

from nonebot.adapters import Bot, Event, Message
from nonebot.adapters.onebot.v11 import Bot as V11Bot
from nonebot.adapters.onebot.v11 import GroupMessageEvent as V11GMEvent
from nonebot.adapters.onebot.v11 import MessageEvent as V11MEvent
from nonebot.adapters.onebot.v12 import Bot as V12Bot
from nonebot.adapters.onebot.v12 import ChannelMessageEvent as V12CMEvent
from nonebot.adapters.onebot.v12 import GroupMessageEvent as V12GMEvent
from nonebot.adapters.onebot.v12 import MessageEvent as V12MEvent


async def get_at_username_onebot_v11(
    bot: V11Bot, event: Event, msg: Message
) -> Optional[str]:
    msg_segs = msg["at"]
    if msg_segs:
        msg_seg = msg_segs[0]
        info = None
        if isinstance(event, V11GMEvent):
            info = await bot.get_group_member_info(
                group_id=event.group_id, user_id=msg_seg.data["qq"]
            )
        elif isinstance(event, V11MEvent):
            info = await bot.get_stranger_info(user_id=msg_seg.data["qq"])
        if info:
            return info.get("card") or info.get("nickname")


async def get_mention_username_onebot_v12(
    bot: V12Bot, event: Event, msg: Message
) -> Optional[str]:
    msg_segs = msg["mention"]
    if msg_segs:
        msg_seg = msg_segs[0]
        info = None
        if isinstance(event, V12GMEvent):
            info = await bot.get_group_member_info(
                group_id=event.group_id, user_id=msg_seg.data["user_id"]
            )
        elif isinstance(event, V12CMEvent):
            info = await bot.get_channel_member_info(
                guild_id=event.guild_id,
                channel_id=event.channel_id,
                user_id=msg_seg.data["user_id"],
            )
        if isinstance(event, V12MEvent):
            info = await bot.get_user_info(user_id=msg_seg.data["user_id"])
        if info:
            return info["user_displayname"] or info["user_name"]


async def get_mention_username(bot: Bot, event: Event, msg: Message) -> Optional[str]:
    if isinstance(bot, V11Bot):
        return await get_at_username_onebot_v11(bot, event, msg)
    elif isinstance(bot, V12Bot):
        return await get_mention_username_onebot_v12(bot, event, msg)


async def get_sender_username_onebot_v11(bot: V11Bot, event: Event) -> Optional[str]:
    assert isinstance(event, V11MEvent)
    return event.sender.card or event.sender.nickname


async def get_sender_username_onebot_v12(bot: V12Bot, event: Event) -> Optional[str]:
    assert isinstance(event, V12MEvent)
    info = await bot.get_user_info(user_id=event.user_id)
    return info["user_displayname"] or info["user_name"]


async def get_sender_username(bot: Bot, event: Event) -> Optional[str]:
    if isinstance(bot, V11Bot):
        return await get_sender_username_onebot_v11(bot, event)
    elif isinstance(bot, V12Bot):
        return await get_sender_username_onebot_v12(bot, event)
