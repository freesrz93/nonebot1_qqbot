from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot.log import logger
from .parser import search_by_keyword, list2str, get_magnets
import asyncio
from nonebot.message import MessageSegment


@on_command('av', aliases=['AV'])
async def av_search(session: CommandSession):
    logger.info('执行 av_search 命令')
    keyword = session.get('keyword', prompt='请输入要搜索的关键词')
    urls, titles = await search_by_keyword(keyword)
    titles_msg = MessageSegment.text(list2str(titles))
    await session.send(titles_msg)
    video_num = session.get('num', prompt='请选择合适的结果序号')
    magnets = await get_magnets(urls[video_num])  # magnets: List[Tuple(str, str)]
    magnets_ = [' '.join(x) for x in magnets]
    magnets_msg = MessageSegment.text('\n'.join(magnets_))
    await session.send(magnets_msg)
