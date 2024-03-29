#    OpenLightBit-KuoHuBit
#    Copyright (C) 2024  Emerald-AM9
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

from graia.ariadne.event.mirai import NewFriendRequestEvent, BotInvitedJoinGroupRequestEvent
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from loguru import logger
from graia.saya.channel import ChannelMeta

import botfunc

channel = Channel[ChannelMeta].current()
channel.meta['name'] = "自身信息处理"
channel.meta['description'] = "处理例如加群请求等事件"
channel.meta['author'] = "KuoHu"

# 好友添加
@channel.use(
    ListenerSchema(
        listening_events=[NewFriendRequestEvent]
    )
)
async def new_friend(event: NewFriendRequestEvent):
    if botfunc.get_config('NewFriendRequestEvent'):
        await event.accept()
        logger.success(
            f'已允许 {event.supplicant}（{event.nickname}） 对 Bot 的加好友请求'
        )
    else:
        await event.reject()
        logger.info(
            f'已阻止 {event.supplicant}（{event.nickname}） 对 Bot 的加好友请求'
        )


# 邀请加群
@channel.use(
    ListenerSchema(
        listening_events=[BotInvitedJoinGroupRequestEvent]
    )
)
async def new_friend(event: BotInvitedJoinGroupRequestEvent):
    if botfunc.get_config('BotInvitedJoinGroupRequestEvent'):
        await event.accept()
        logger.success(
            f'已允许 {event.supplicant}（{event.nickname}） 将 Bot 邀请进群 {event.source_group}（{event.group_name}）'
        )
    else:
        await event.reject()
        logger.info(
            f'已阻止 {event.supplicant}（{event.nickname}） 将 Bot 邀请进群 {event.source_group}（{event.group_name}）'
        )
