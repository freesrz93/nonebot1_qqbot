# -*-coding:utf8-*-


import nonebot
from .history import history
from nonebot.log import logger
from bilibili_api import user, dynamic
from nonebot.message import MessageSegment
import time
from config import DYNAMIC_INTERVAL

group_list = [857743425]
user_list = {205889201: '碧蓝海事局', 233114659: '碧蓝航线', 436344151: 'xnxnsrz'}


@nonebot.scheduler.scheduled_job('interval', seconds=DYNAMIC_INTERVAL)
async def _():
    bot = nonebot.get_bot()
    now_time = time.time()
    for dynamic_id in history:
        if now_time - history[dynamic_id] > 3 * DYNAMIC_INTERVAL:
            history.pop(dynamic_id)
    for user_uid in user_list:
        logger.info(f'获取[{user_list[user_uid]}]的动态')
        dynamic_messages = get_latest_dynamic(user_uid, now_time)
        for group_id in group_list:
            for message in dynamic_messages:
                logger.info(f'向群[{group_id}]发送动态信息')
                await bot.send_group_msg(group_id=group_id, message=message)


def get_latest_dynamic(uid: int, now_time: float):
    dynamic_list = user.get_dynamic_g(uid)
    while True:
        latest_dynamic = next(dynamic_list)
        timestamp = latest_dynamic['desc']['timestamp']
        dynamic_id = latest_dynamic['desc']['dynamic_id']
        if now_time - timestamp <= 1.8 * DYNAMIC_INTERVAL and dynamic_id not in history:
            history[dynamic_id] = timestamp
            yield dynamic2message(latest_dynamic)
            continue
        break


def dynamic2message(dynamic_dict: dict):
    """
    将从api获取到的原始动态转换为消息
    """
    author_name = dynamic_dict['desc']['user_profile']['info']['uname']
    dynamic_id = dynamic_dict['desc']['dynamic_id']
    if dynamic_dict['desc']['type'] == 1:  # 转发或投票
        text = f"用户[{author_name}]转发了动态：\n" + dynamic_dict['card']['item']['content'] + "\n---------------------\n"
        origin_dynamic = dynamic.get_info(dynamic_dict['card']['item']['orig_dy_id'])
        ori_message = dynamic2message(origin_dynamic)
        msg = MessageSegment.text(text) + ori_message

    elif dynamic_dict['desc']['type'] == 2:  # 图文动态
        text = f"用户[{author_name}]发布了动态：\n" + dynamic_dict['card']['item']['description']
        msg = MessageSegment.text(text)
        for i in range(dynamic_dict['card']['item']['pictures_count']):
            msg += MessageSegment.image(dynamic_dict['card']['item']['pictures'][i]['img_src'])

    elif dynamic_dict['desc']['type'] == 4:  # 纯文字动态
        msg = MessageSegment.text(f"用户[{author_name}]发布了动态：\n" + dynamic_dict['card']['item']['content'])

    elif dynamic_dict['desc']['type'] == 8:  # 视频投稿
        msg = MessageSegment.text(f"用户[{author_name}]发布了视频：\n" + dynamic_dict['card']['dynamic'] \
                                  + "\n视频链接：" + dynamic_dict['card']['short_link'])

    elif dynamic_dict['desc']['type'] == 64:  # 发布专栏
        msg = MessageSegment.text(f"用户[{author_name}]发布了专栏：\n" + dynamic_dict['card']['title'])
    else:
        msg = MessageSegment.text('')
    msg += MessageSegment.text(f'\n\n原动态链接：https://t.bilibili.com/{dynamic_id}')
    return msg


if __name__ == "__main__":
    pass
