# nonebot1_qqbot 文档

[![License](https://img.shields.io/github/license/nonebot/nonebot.svg)](LICENSE)
![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)
[![QQ](https://img.shields.io/badge/QQ-1526334563-brightgreen)](http://wpa.qq.com/msgrd?v=3&uin=1526334563&site=qq&menu=yes)

## 说明

本机器人基于 [nonebot](https://github.com/nonebot/nonebot), qq客户端则使用 [go-cqhttp](https://github.com/Mrs4s/go-cqhttp)   
本人写此机器人纯为娱乐及给~~饥渴难耐的~~群友整活. 我并非专业人士, 代码可能并不好看, 文档尽量写写, 主要是为了我自己以后能看懂, 也谈不上规范. 不过如果 有人想要探讨 nonebot 机器人的相关问题~~以及可能的提交pr(
盲猜不会有)~~, 欢迎联系我.

## 使用

* 下载并配置 [go-cqhttp](https://github.com/Mrs4s/go-cqhttp)
* git clone https://github.com/freesrz93/nonebot1_qqbot.git
* 安装 requirements.txt
* 配置 config.py.simple, 更名为 config.py
* 运行 go-cqhttp, bot.py
* ~~面对 bug 吧少年~~

## 已实现功能

* **setu功能 —— setu**
  > 计划加入~~指定张数(一张就够了, 别冲了)和关键词搜索功能~~(独立为p站搜图功能)  
  > ~~现阶段加载速度慢且不稳定, 原因是该功能需要即时下载图片, 且需要代理~~  
  > (已实现) 想到的比较理想的改进方式：每次调用时发送一张本地图, 然后删除这张图, 而后下载一张新图  
  > 新的问题：虽然可以保证发图及时, 但发图后的下载过程耗时较长, 在这段时间内同一个群无法
  > 再次调用此功能, 不仅如此, 此时收到任何其他消息机器人都会出现奇奇怪怪的反应
  > (其他群不受影响, 应该是一个群对应一个 session)  
  > (已实现)解决方案：将下载程序独立运行, setu 命令仅从本地取图并发送,
  > 但此方法需定期手动执行下载, 较麻烦。  
  > (已实现)最终解决方案：靠 pixiv 爬虫(异步或多线程)大量取图, 并设定定时任务
  > 此处指路 [PixivUtil2](https://github.com/Nandaka/PixivUtil2) , 具体设置请自行研究
* **番号给磁力 —— AV_Searcher**
  > 此功能似乎容易被风控, 导致机器人无法在群里发送大段标题和磁链消息
* **B站动态 —— bilibili_dynamic(测试中)**
  > 感谢[QQBot_bilibili](https://github.com/wxz97121/QQBot_bilibili)
* **胡言乱语 —— hyly**
  > 对各种乱七八糟的语句的回复  
  > 目前已实现：
  > * 二刺螈圣经

## 待实现功能

* **机器人帮助 —— helper**
  > 自我介绍、功能列表、命令帮助
* **复读 —— repeat**
  > 当在15s(暂定)内出现连续两条相同消息时复读
* **报时 —— clock**
  > 整点报时, ~~多时区~~(copy 了一段别人的代码, 尚未研究修改)
* **撤回消息提醒 —— chehui**

> 以下功能需寻找合适 API, 否则只能通过爬虫, 可能效率较低

* **pixiv搜索或id给图 —— pixiv**
* **steam 搜索指定游戏 —— steam_search**

> 以下内容少儿不宜

* **女优信息（暂无合适数据源）**




