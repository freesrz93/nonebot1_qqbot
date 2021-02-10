import os
import nonebot
import config


if __name__ == '__main__':
    nonebot.init(config)
    nonebot.load_builtin_plugins()
    nonebot.load_plugins(os.path.join(os.getcwd(), 'nonebot1_qqbot', 'plugins'), 'nonebot1_qqbot.plugins')
    nonebot.run()
