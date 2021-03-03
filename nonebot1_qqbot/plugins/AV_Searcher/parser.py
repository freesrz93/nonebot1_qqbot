import re
import traceback

import httpx
from bs4 import BeautifulSoup
from nonebot.log import logger

from config import PROXY


async def get_html(url, params=None, timeout=5, headers=None) -> str:
    """
    即加入了异常处理的 httpx.AsyncClient.get() 方法，省略了不常用参数，返回 httpx.Response.text
    \n若捕获异常不会抛出，而是返回空字符串
    """
    if not headers:
        headers = {
            "User-Agent":
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3100.0 Safari/537.36"
        }
    try:
        async with httpx.AsyncClient(proxies=PROXY, timeout=timeout, headers=headers) as client:
            r = await client.get(url, params=params)
            r = r.text
    except httpx.ProxyError:
        logger.error(f'请求 url ({url}) 时 Proxy 出错，请检查代理设置 ')
        return ''
    except httpx.RequestError:
        logger.error(f'请求 url ({url}) 时发生错误')
        traceback.print_exc()
        return ''
    except httpx.HTTPStatusError:
        logger.error(f'请求 url ({url}) 返回了错误的状态码：{r.status_code}')
        return r
    return r


async def search_by_keyword(keyword: str) -> (list, list):
    """
    给定关键词，从网站上获取搜索结果，返回分别由结果url及结果标题组成的两个列表

    """

    params = {'q': keyword, 'f': 'download'}
    html_code = await get_html('https://javdb.com/search', params=params)  # r: httpx.Response
    soup = BeautifulSoup(html_code, 'lxml')  # 解析搜索结果页 html 代码
    true_urls, titles = [], []
    x = soup('div', class_="grid-item column")  # x: 结果页上所有结果小方块的源代码
    if x:  # 搜索结果
        for res in x:
            try:
                true_url = res.a['href']  # 表示该影片的详情页 url, e.g. /v/JAy0B  完整 url 应为 https://javdb.com/v/JAy0B
                title = res.a['title']  # 影片标题
                av_nums = list(res.a('div', class_='uid'))  # 可能为番号的文本列表
                av_num = av_nums[0].string.strip() + ' '  # 番号
            except:
                logger.error('解析 html 元素失败')
                true_url, av_num, title = '', '', ''
            true_urls.append(true_url)
            titles.append(av_num + title)
        return true_urls, titles
    else:
        logger.info(f'未搜索到{keyword}相关影片')
        return [], []


async def get_magnets(ture_url: str) -> list:
    """
    从影片详情页 url e.g. /v/JAy0B 获得该影片的所有磁链及其信息组成的列表
    """
    magnets = []
    full_url = 'https://javdb.com' + ture_url
    html_code = await get_html(full_url)  # r: httpx.Response
    soup = BeautifulSoup(html_code, 'lxml')
    try:
        for text in soup('a', title="右鍵點擊並選擇「複製鏈接地址」"):
            url = re.sub(r'&dn=.*', '', text['href'])
            url_info = '  '.join([re.sub(r'[()\s]', '', x) for x in list(text.stripped_strings)[1:]])
            # 磁链信息，如文件大小，有无字幕等
            magnets.append((url, url_info))
        return magnets
    except:
        return []


def list2str(lst: list) -> str:
    """
    将 list 内的元素转化为字符串，使得打印时能够按行输出并在前面加上序号(从1开始)

    e.g.
    In:
    lst = [a,b,c]
    str = list2str(lst)
    print(str)

    Out:
    1. a
    2. b
    3. c
    """
    i = 1
    res_list = []
    for x in lst:
        res_list.append(str(i)+'. '+str(x))
        i += 1
    res_str = '\n'.join(res_list)
    return res_str
