bl_info = {
    'name': 'Easy Bake Node',
    'author': '会飞的键盘侠',
    'version': (0, 0, 1),
    'blender': (3, 0, 0),
    'location': '3DView->Panel',
    'category': '辣椒出品',
    'doc_url': "https://bing.com"
}

import sys
import bpy
from .src import register as reg
from .src import unregister as unreg
from .utils.logger import logger
from .utils.timer import timer_reg, timer_unreg
from .utils.watcher import watcher_reg, watcher_unreg


def register():
    logger.debug(f'{bl_info["name"]}: register')
    reg()
    timer_reg()
    watcher_reg()


def unregister():
    logger.debug(f'{bl_info["name"]}: unregister')
    unreg()
    watcher_unreg()
    timer_unreg()
    modules_update()


def modules_update():
    from .utils.logger import logger
    logger.close()
    for i in list(sys.modules):
        if not i.startswith(__package__) or i == __package__:
            continue
        del sys.modules[i]
    del sys.modules[__package__]
