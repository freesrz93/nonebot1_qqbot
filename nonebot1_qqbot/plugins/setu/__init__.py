import os
import random
import shutil

from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot.log import logger
from nonebot.message import MessageSegment
from nonebot.typing import Message_T

from config import RES_DIR
from .get_setu2local import get_setu2local


@on_command('setu', privileged=True)
async def setu(session: CommandSession):
    logger.info('执行setu命令')
    image_msg, name = get_local_setu()
    await session.send(name)
    await session.send(image_msg)
    logger.info(f'向QQ客户端发送了内容：{image_msg}')
    # await get_setu2local()


# on_natural_language 装饰器将函数声明为一个自然语言处理器
# keywords 表示需要响应的关键词，类型为任意可迭代对象，元素类型为 str
# 如果不传入 keywords，则响应所有没有被当作命令处理的消息
@on_natural_language(keywords={'涩图', '色图'})
async def _(session: NLPSession):
    # 返回意图命令，前两个参数必填，分别表示置信度和意图命令名
    return IntentCommand(90.0, 'setu')


PLU_RES_DIR = RES_DIR + '/setu'


def get_local_setu() -> (Message_T, str):
    """
    从本地资源目录随机取一张涩图，将其移动到sent文件夹，返回该图生成的消息链对象
    """
    try:
        f = os.scandir(PLU_RES_DIR + '/images')  # f: iterable
        files = [file for file in f if file.is_file()]  # list[os.DirEntry]
        file = random.choice(files)  # os.DirEntry
        name = file.name
        shutil.move(file.path, PLU_RES_DIR + '/images/sent')
        return MessageSegment.image('file:///' + PLU_RES_DIR + f'/images/sent/{name}'), name
    except:
        logger.info('取得本地涩图失败，将发送随机默认图片')
        name = 'default/' + random.choice(os.listdir(PLU_RES_DIR + '/images/default'))
        return MessageSegment.image('file:///' + PLU_RES_DIR + f'/images/default/{name}'), ''
