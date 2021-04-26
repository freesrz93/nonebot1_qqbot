# -*-coding:utf8-*-


import nonebot
from nonebot.log import logger
from bilibili_api import user, dynamic
from nonebot.message import MessageSegment
import time
from config import DYNAMIC_INTERVAL, USER_LIST, GROUP_LIST

HISTORY = {}


@nonebot.scheduler.scheduled_job('interval', seconds=DYNAMIC_INTERVAL)
async def _():
    bot = nonebot.get_bot()
    now_time = time.time()
    for dynamic_id in list(HISTORY):
        if now_time - HISTORY[dynamic_id] > 3 * DYNAMIC_INTERVAL:
            HISTORY.pop(dynamic_id)
    for user_uid in USER_LIST:
        if str(now_time).endswith('1'):
            logger.info(f'获取[{USER_LIST[user_uid]}]的动态')
        dynamic_messages = get_latest_dynamics(user_uid, now_time)
        if dynamic_messages:
            for group_id in GROUP_LIST:
                for message in dynamic_messages:
                    logger.info(f'向群[{group_id}]发送b站动态')
                    await bot.send_group_msg(group_id=group_id, message=message)


def get_latest_dynamics(uid: int, now_time: float):
    dynamic_list = user.get_dynamic_g(uid)
    msg_list = []
    for latest_dynamic in dynamic_list:
        timestamp = latest_dynamic['desc']['timestamp']
        dynamic_id = latest_dynamic['desc']['dynamic_id']
        if now_time - timestamp <= 1.8 * DYNAMIC_INTERVAL and dynamic_id not in HISTORY:
            HISTORY[dynamic_id] = timestamp
            msg_list.append(dynamic2message(latest_dynamic))
            continue
        break
    return msg_list


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
