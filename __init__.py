
import sys
import bpy
from .src import register as reg
from .src import unregister as unreg
from .utils.logger import logger
from .utils.timer import timer_reg, timer_unreg
from .utils.watcher import watcher_reg, watcher_unreg


def register():
    reg()
    timer_reg()
    watcher_reg()


def unregister():
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
