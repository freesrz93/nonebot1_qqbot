# noinspection PyUnresolvedReferences
import asyncio
import os
import random
import shutil
import time
import traceback
from os import path

import aiofiles
import httpx
import ujson
from nonebot.log import logger
from nonebot.message import MessageSegment
from nonebot.typing import Message_T

from config import SETU_API, PROXY, RES_DIR

PLU_RES_DIR = RES_DIR + '/setu'


def get_local_setu() -> Message_T:
    """
    从本地资源目录随机取一张涩图，将其移动到sent文件夹，返回该图生成的消息链对象
    """
    try:
        f = os.scandir(PLU_RES_DIR + '/images')  # f: iterable
        files = [file for file in f if file.is_file()]  # list[os.DirEntry]
        file = random.choice(files)  # os.DirEntry
        name = file.name
        shutil.move(file.path, PLU_RES_DIR + '/images/sent')
        return MessageSegment.image('file:///' + PLU_RES_DIR + f'/images/sent/{name}')
    except:
        logger.info('取得本地涩图失败，将发送随机默认图片')
        name = 'default/' + random.choice(os.listdir(PLU_RES_DIR + '/images/default'))
        return MessageSegment.image('file:///' + PLU_RES_DIR + f'/images/default/{name}')


async def get_setu2local(r18: int = 0,
                         num: int = 1,
                         proxy: str = 'i.pixiv.cat',
                         size1200: bool = False) -> None:
    """
    向本地保存一张涩图
    \n在目前的所有调用中，该函数的参数均使用缺省值

    :param r18: 0为非R18，1为R18，2为混合
    :param num: 一次返回的结果数量，范围为1到10，不提供APIKEY时固定为1；在指定关键字的情况下，结果数量可能会不足指定的数量
    :param proxy: 设置返回的原图链接的域名，你也可以设置为disable来得到真正的原图链接
    :param size1200: 是否使用master_1200缩略图，即长或宽最大为1200px的缩略图，以节省流量或提升加载速度（某些原图的大小可以达到十几MB）
    """
    logger.info('向本地补充 setu 中...')
    params = {'apikey': SETU_API, 'r18': r18, 'num': num, 'proxy': proxy, 'size1200': size1200}
    try:
        s = time.time()
        r = await request_api(params)
        setu = r['data'][0]
        pid = setu['pid']
        url = setu['url']
        title = setu['title']
        name = path.basename(url)
        await save_image(url=url, name=name)
        e = time.time()
        logger.info(f'补充 setu 成功, 用时{e - s:.3f}s')
    except:
        logger.error('补充 setu 出错')
        traceback.print_exc()


async def request_api(params) -> dict:
    """
    本函数中异常处理均不抛出
    请求setu API, 返回 dict, 包含以下字段:
    {'code': int,               #返回码
    'msg': str,                 #错误信息
    'quota': int,               #剩余调用次数
    'quota_min_ttl': int,       #距下次调用次数+1的秒数
    'count': int,               #结果数
    'data': setu[]}             #setu数组

    其中 setu[] 包含以下字段:
    [{'pid': int, 'p': int, 'uid': int,     #作品pid，作品在几p，作者uid
    'title': str,                           #标题
    'author': str,                          #作者名
    'url': str,                             #图片链接
    'r18': bool,                            #是否r18
    'width': int, 'height': int,            #图片宽高
    'tags': list[str]                       #标签，包括中文（如果有）
    }]
    """
    try:
        async with httpx.AsyncClient(proxies=PROXY, timeout=3) as client:
            r = await client.get('https://api.lolicon.app/setu/', params=params)
            r = ujson.loads(r.text)
    except httpx.ProxyError:
        logger.error('请求 setu API (https://api.lolicon.app/setu/) 时 Proxy 出错，请检查代理设置 ')
        return {}
    except httpx.RequestError:
        logger.error('请求 setu API (https://api.lolicon.app/setu/) 时发生错误')
        traceback.print_exc()
        return {}
    if r['code'] is not 0:
        logger.warning(f'setu API 未返回图片链接，异常状态码 {r["code"]}：{r["msg"]}')
        return {}
    return r


async def save_image(url: str, name: str) -> None:
    """
    从url地址下载图片，保存到 ./images 目录，请注意：本函数中网络请求不会超时
    \n本函数中的异常处理均抛出

    :param url: 图片地址
    :param name: 保存到本地时的文件名（包括扩展名）
    """
    try:  # 请求图片
        async with httpx.AsyncClient(proxies=PROXY, timeout=None) as client:
            r = await client.get(url)
            img = r.content
    except httpx.ProxyError:
        logger.error(f'请求 setu ({url}) 时 Proxy 出错，请检查代理设置 ')
        raise httpx.ProxyError
    except httpx.RequestError:
        logger.error(f'请求 setu ({url}) 时发生错误')
        traceback.print_exc()
        raise httpx.RequestError
    except httpx.HTTPStatusError:
        logger.warning(f'setu ({url}) 返回了错误的状态码：{r.status_code}')
        raise httpx.HTTPStatusError
    try:  # 写入到文件
        async with aiofiles.open(PLU_RES_DIR + f'/images/{name}', mode='wb') as f:
            await f.write(img)
    except:
        logger.error(f'将 setu {name} 保存到本地时发生错误')
        traceback.print_exc()
        raise IOError


if __name__ == '__main__':
    import asyncio

    res = asyncio.run(get_setu2local())
    print(res)
