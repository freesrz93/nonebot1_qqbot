"""
此脚本原本负责执行 setu 命令的一部分功能，用于下载涩图到本地，由于其运行可能较缓慢（取决于网络环境），导致 setu 命令执行缓慢，造成会话阻塞
因此现在 setu 命令已不引用此功能，临时解决方案，只能定时手动执行此脚本下载图片，setu 执行时则只从本地取图

3.3更新：建议使用其他工具获取图片，此脚本很弱
"""
import logging
import time
import traceback
from os import path

import aiofiles
import httpx
import ujson

from config import SETU_API, PROXY, RES_DIR

PLU_RES_DIR = RES_DIR + '/setu'
logger = logging.getLogger('setu')
logger.setLevel('INFO')


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
    logging.info('向本地补充 setu 中...')
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
    if r['code'] != 0:
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
    for _ in range(10):
        res = asyncio.run(get_setu2local())
