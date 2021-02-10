from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot.log import logger
from .data_source import get_setu, get_setu_local
import asyncio


@on_command('setu')
async def setu(session: CommandSession):
    logger.info('执行setu命令')
    image = get_setu_local()
    await session.send(image)
    logger.info(f'向QQ客户端发送了内容：{image}')
    image = await get_setu()
    logger.info(f'将 setu {name}保存到本地')


# on_natural_language 装饰器将函数声明为一个自然语言处理器
# keywords 表示需要响应的关键词，类型为任意可迭代对象，元素类型为 str
# 如果不传入 keywords，则响应所有没有被当作命令处理的消息
@on_natural_language(keywords={'涩图', '色图'})
async def _(session: NLPSession):
    # 返回意图命令，前两个参数必填，分别表示置信度和意图命令名
    return IntentCommand(90.0, 'setu')
