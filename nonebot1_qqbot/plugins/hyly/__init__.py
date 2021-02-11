from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot.log import logger
from nonebot.argparse import ArgumentParser
from nonebot.message import MessageSegment
from .ecysj import ecysj
import random


# -----二刺螈圣经--------
@on_command('ecysj')
async def _(session: CommandSession):
    logger.info('发送 二次元圣经 ！')
    x = random.choice(ecysj.split('\n'))
    await session.send(MessageSegment.text(x))


@on_natural_language(keywords=['二次元圣经', '二刺螈圣经'], only_to_me=False)
async def _(session: NLPSession):
    return IntentCommand(100, 'ecysj')
# ---------------------








