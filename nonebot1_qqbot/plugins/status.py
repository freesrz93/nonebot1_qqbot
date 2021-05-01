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
    create_time = p.create_time()
    now_time = time.time()
    run_time = now_time - create_time
    m, s = divmod(run_time, 60)
    h, m = divmod(int(m), 60)
    d, h = divmod(h, 24)
    # 内存 cpu 占用
    mem = p.memory_percent()
    cpu = p.cpu_percent()
    res = f'[Bot Status]\n已运行：{d}天{h}时{m}分{s:.2f}秒\n内存：{mem:.2f}%\nCPU：{cpu:.2f}%'
    return res

