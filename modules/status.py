import platform

import cpuinfo
import psutil
from graia.amnesia.message import MessageChain
from graia.ariadne import Ariadne
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.element import At, Plain
from graia.ariadne.message.parser.base import MatchContent
from graia.ariadne.model import Group
from graia.saya import Channel
from graia.saya.builtins.broadcast import ListenerSchema
from graia.saya.channel import ChannelMeta

channel = Channel[ChannelMeta].current()
channel.meta['name'] = "运行状态"
channel.meta['description'] = "获取Bot运行状态"
channel.meta['author'] = "Abjust"


# 监听群消息（!status）
@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        decorators=[MatchContent("状态")]
    )
)
# 收到消息，检查信息消息并发送
async def status(app: Ariadne, event: GroupMessage, group: Group):
    await app.send_message(
        group,
        MessageChain([
            At(event.sender),
            Plain("\n"),
            Plain("OpenLightBit 运行信息\n"
                  f"运行环境版本：Python {platform.python_version()}\n"
                  f"系统版本：{platform.uname().system} {platform.uname().version}\n"
                  f"CPU：{cpuinfo.get_cpu_info()['brand_raw']} （占用率 {psutil.cpu_percent()} %）\n"
                  f"剩余RAM：{psutil.virtual_memory().free / 1048576:.2f} / "
                  f"{psutil.virtual_memory().total / 1048576:.2f} MB\n"
                  f"剩余Swap：{psutil.swap_memory().free / 1048576:.2f} / "
                  f"{psutil.swap_memory().total / 1048576:.2f} MB\n"
                  f"剩余存储空间：{psutil.disk_usage('/').free / 1073741824:.2f} / "
                  f"{psutil.disk_usage('/').total / 1073741824:.2f} GB")
        ])
    )
