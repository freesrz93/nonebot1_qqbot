from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand
from nonebot.log import logger
from .parser import search_by_keyword, list2str, get_magnets
from nonebot.argparse import ArgumentParser
from nonebot.message import MessageSegment


@on_command('av', aliases=['AV'], only_to_me=False)
async def av_search(session: CommandSession):
    logger.info('执行 av_search 命令')
    try:
        keyword = session.state['keyword']
    except:
        session.finish(MessageSegment.text('语句错误：缺少搜索关键词\n请重新调用功能'))
        return
    urls, titles = await search_by_keyword(keyword)
    if session.is_first_run:
        titles_msg = MessageSegment.text(list2str(titles[0:4]))  # 避免结果过多刷屏，只输出前5条
        logger.info('发送搜索结果')
        await session.send(titles_msg)
    video_num = session.get('num', prompt='请选择合适的结果序号')
    try:
        true_url = urls[int(video_num)-1]
    except:
        true_url = urls[0]
        logger.info('用户输入参数非法')
        await session.send(MessageSegment.text('输入的序号非法，只好返回第一个结果啦，呐呐呐'))
    magnets = await get_magnets(true_url)  # magnets: List[Tuple(str, str)]
    magnets_ = [' '.join(x) for x in magnets]
    magnets_msg = MessageSegment.text('\n'.join(magnets_[0:4]))  # 避免磁链太多刷屏
    logger.info('发送磁链列表')
    await session.send(magnets_msg)


@av_search.args_parser
async def _(session: CommandSession):
    # 去掉消息首尾的空白符
    stripped_arg = session.current_arg_text.strip()

    if session.is_first_run:
        # 该命令第一次运行（第一次进入命令会话）
        if stripped_arg:
            # 第一次运行参数不为空，意味着用户直接将参数跟在命令名后面，作为参数传入
            session.state['keyword'] = stripped_arg
            session.state['user'] = session.event.user_id  # 调用此命令的原始用户
        return

    if not stripped_arg:
        # 用户没有发送有效的参数（而是发送了空白字符），则提示重新输入
        # 这里 session.pause() 将会发送消息并暂停当前会话（该行后面的代码不会被运行）
        session.pause('请输入keyword')

    # 如果当前正在向用户询问更多信息（例如本例中的要查询的城市），且用户输入有效，则放入会话状态
    session.state[session.current_key] = stripped_arg


