from nonebot.message import MessageSegment
import os
import time
import psutil
from nonebot.log import logger
from nonebot import on_command, CommandSession, permission


@on_command('bot_status', aliases='status', permission=permission.SUPERUSER)
async def reload_plugins(session: CommandSession):
    status = get_my_status()
    logger.info('发送Bot状态')
    await session.send(MessageSegment.text(status))


def get_my_status():
    pid = os.getpid()
    p = psutil.Process(pid)
    # 运行时间
    create_time = time.localtime(p.create_time())
    time.sleep(5)
    now_time = time.localtime(time.time())
    _, _, d, h, m, s, _, _, _ = [y-x for x, y in zip(create_time, now_time)]
    # 内存 cpu 占用
    mem = p.memory_percent()
    cpu = p.cpu_percent()
    res = f'[Bot Status]\n已运行：{d}天{h}时{m}分{s}秒\n内存：{mem:.2}%\nCPU：{cpu:.2}%'
    return res

