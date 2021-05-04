import os
import random
import shutil
import time

from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot.log import logger
from nonebot.message import MessageSegment

from config import SUPERUSERS, SETU, RES_DIR

HISTORY = {}  # 储存上次调用时间


@on_command('setu', privileged=True)
async def setu(session: CommandSession):
    now_time = time.time()
    if is_permitted(session.event.user_id, now_time):
        logger.info(f'[{session.event.user_id}]允许调用！')
        HISTORY[session.event.user_id] = now_time
        image_msg = get_local_setu()
        await session.send(image_msg)
        logger.info(f'发送[{image_msg}]')
    else:
        logger.info(f'[{session.event.user_id}]拒绝调用！')
        await session.send(MessageSegment.text('调用频率过高！') + MessageSegment.at(session.event.user_id))


@on_natural_language(keywords={'涩图', '色图'})
async def _(session: NLPSession):
    # 返回意图命令，前两个参数必填，分别表示置信度和意图命令名
    return IntentCommand(90.0, 'setu')


PLU_RES_DIR = RES_DIR + '/setu'


def get_local_setu():
    """
    从本地资源目录随机取一张涩图，将其移动到sent文件夹，返回该图生成的消息链对象
    """
    try:
        f = os.scandir(PLU_RES_DIR + '/images')  # f: iterable
        files = [file for file in f if file.is_file()]  # list[os.DirEntry]
        file = random.choice(files)  # os.DirEntry
        name = file.name
        shutil.move(file.path, PLU_RES_DIR + '/images/sent')
        return MessageSegment.text(name) + MessageSegment.image('file:///' + PLU_RES_DIR + f'/images/sent/{name}')
    except:
        logger.info('取得本地涩图失败，将发送随机默认图片')
        name = random.choice(os.listdir(PLU_RES_DIR + '/images/default'))
        return MessageSegment.image('file:///' + PLU_RES_DIR + f'/images/default/{name}'), ''


def is_permitted(id: int, now_time):
    if id in SUPERUSERS or id in SETU.WHITELIST:
        return True
    elif id in SETU.BLACKLIST:
        return False
    elif id in HISTORY:
        return now_time - HISTORY[id] > SETU.INTERVAL
    return True
