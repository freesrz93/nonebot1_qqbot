# -*-coding:utf8-*-
import asyncio
import time

import nonebot
from bilibili_api import user, dynamic
from nonebot.log import logger
from nonebot.message import MessageSegment, Message

from config import BiliBili

HISTORY = {}


@nonebot.scheduler.scheduled_job('interval', seconds=BiliBili.INTERVAL, max_instances=10,
                                 misfire_grace_time=None)
async def _():
    bot = nonebot.get_bot()
    now_time = time.time()
    for dynamic_id in list(HISTORY):
        if now_time - HISTORY[dynamic_id] > 3 * BiliBili.INTERVAL:
            logger.info(f'从[HISTORY]删除[{dynamic_id}, {HISTORY[dynamic_id]}]')
            HISTORY.pop(dynamic_id)
    logger.info(f'获取[{len(BiliBili.USER_LIST)}]个up的动态')
    for user_uid in BiliBili.USER_LIST:
        dynamic_messages = get_latest_dynamics(user_uid, now_time)
        if dynamic_messages:
            tasks = []
            for group_id in BiliBili.GROUP_LIST:
                for message in dynamic_messages:
                    logger.info(f'向群[{group_id}]发送b站动态')
                    tasks.append(bot.send_group_msg(group_id=group_id, message=message))
            await asyncio.gather(*tasks)


def get_latest_dynamics(uid: int, now_time: float):
    dynamic_list = user.get_dynamic_g(uid)
    msg_list = []
    for latest_dynamic in dynamic_list:
        timestamp = latest_dynamic['desc']['timestamp']
        dynamic_id = latest_dynamic['desc']['dynamic_id']
        if now_time - timestamp <= 1.8 * BiliBili.INTERVAL and dynamic_id not in HISTORY:
            HISTORY[dynamic_id] = timestamp
            logger.info(f'向[HISTORY]添加[{dynamic_id}, {HISTORY[dynamic_id]}]')
            msg_list.append(dynamic2message(latest_dynamic))
            continue
        break
    return msg_list


def dynamic2message(dynamic_dict: dict) -> Message:
    """
    将从api获取到的原始动态转换为消息
    """
    author_name = dynamic_dict['desc']['user_profile']['info']['uname']
    dynamic_id = dynamic_dict['desc']['dynamic_id']
    if dynamic_dict['desc']['type'] == 1:  # 转发或投票
        text = f"用户[{author_name}]转发了动态：\n" + dynamic_dict['card']['item']['content'] + "\n---------------------\n"
        origin_dynamic = dynamic.get_info(dynamic_dict['card']['item']['orig_dy_id'])
        ori_message = dynamic2message(origin_dynamic)
        msg = MessageSegment.text(text) + ori_message + MessageSegment.text('\n---------------------')

    elif dynamic_dict['desc']['type'] == 2:  # 图文动态
        text = f"用户[{author_name}]发布了动态：\n" + dynamic_dict['card']['item']['description']
        msg = MessageSegment.text(text)
        for i in range(dynamic_dict['card']['item']['pictures_count']):
            msg = msg + MessageSegment.image(dynamic_dict['card']['item']['pictures'][i]['img_src'])

    elif dynamic_dict['desc']['type'] == 4:  # 纯文字动态
        msg = MessageSegment.text(f"用户[{author_name}]发布了动态：\n" + dynamic_dict['card']['item']['content'])

    elif dynamic_dict['desc']['type'] == 8:  # 视频投稿
        msg = MessageSegment.text(
            f"用户[{author_name}]发布了视频：\n" + dynamic_dict['card']['dynamic'] + "\n视频标题：" + dynamic_dict['card'][
                'title'] + "\n视频链接：" + dynamic_dict['card']['short_link'])

    elif dynamic_dict['desc']['type'] == 64:  # 发布专栏
        msg = MessageSegment.text(f"用户[{author_name}]发布了专栏：\n" + dynamic_dict['card']['title'])
    else:
        msg = MessageSegment.text(f'用户[{author_name}]发布了动态，但无法判断类型')
    msg = msg + MessageSegment.text(f'\n\n原动态链接：https://t.bilibili.com/{dynamic_id}')
    return msg


if __name__ == "__main__":
    pass
