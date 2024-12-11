from queue import Queue
import traceback
import threading
import time
import bpy
from ...utils.timer import Timer


class TaskExecutor:
    tasks = Queue()

    process = {
        "tnum": 0,
        "etask_p": 0,
        "enode_p": 0,
        "etask": "",
        "enode": "",
    }

    running = False

    from ...utils.logger import logger

    _logger = logger

    _handler = None

    _log_prefix = []
    _log_suffix = []

    @classmethod
    def start_server(cls):
        if cls.running:
            return
        cls.running = True
        cls._handler = threading.Thread(target=cls.run, daemon=True)
        cls._handler.start()

    @classmethod
    def run(cls):
        try:
            cls._run()
        except Exception:
            traceback.print_exc()
        cls.running = False

    @classmethod
    def _run(cls):
        from .node_tree import TNodeTree
        while cls.running:
            time.sleep(0.1)
            if cls.tasks.empty():
                continue
            task = cls.tasks.get()
            tree = task.pop("Tree", None)

            @Timer.wait_run
            def f():
                if not tree:
                    return
                tree.is_running = True

            f()
            try:
                TNodeTree.execute_task(cls, task)
            finally:
                @Timer.wait_run
                def f():
                    if not tree:
                        return
                    tree.is_running = False

                f()
            cls.task_done(task)

    @classmethod
    def task_done(cls, task):
        cls.update_queue_num()
        cls.set_current_tree("")
        cls.set_exe_node("")
        cls.update_node_process(0)
        cls.update_tree_process(0)

    @classmethod
    def set_current_tree(cls, tree):
        cls.process["etask"] = str(tree)
        bpy.context.window_manager.bake_tree.etask = str(tree)

    @classmethod
    def update_tree_process(cls, process):
        if not isinstance(process, (str, int, float)):
            return
        cls.process["etask_p"] = process
        bpy.context.window_manager.bake_tree.etask_p = process * 100
        # cls.debug("执行进度: {%s}", cls.process)

    @classmethod
    def set_exe_node(cls, node):
        cls.process["enode"] = str(node)
        bpy.context.window_manager.bake_tree.enode = str(node)

    @classmethod
    def update_node_process(cls, process):
        if not isinstance(process, (str, int, float)):
            return
        cls.process["enode_p"] = process
        bpy.context.window_manager.bake_tree.enode_p = process * 100
        # cls.debug("执行进度: {%s}", cls.process)

    @classmethod
    def end_server(cls):
        cls.running = False
        cls.clear_tasks()

    @classmethod
    def clear_tasks(cls):
        while not cls.tasks.empty():
            cls.tasks.get()
        cls.update_queue_num()

    @classmethod
    def submit_task(cls, task):
        cls.tasks.put(task)
        cls.update_queue_num()

    @classmethod
    def update_queue_num(cls):
        cls.process["tnum"] = cls.tasks.qsize()

    @classmethod
    def push_log_prefix(cls, prefix):
        cls._log_prefix.append(str(prefix))

    @classmethod
    def pop_log_prefix(cls):
        if not cls._log_prefix:
            return
        cls._log_prefix.pop()

    @classmethod
    def clear_prefix(cls):
        cls._log_prefix.clear()

    @classmethod
    def push_log_suffix(cls, suffix):
        cls._log_suffix.append(str(suffix))

    @classmethod
    def pop_log_suffix(cls):
        if not cls._log_suffix:
            return
        cls._log_suffix.pop()

    @classmethod
    def clear_suffix(cls):
        cls._log_suffix.clear()

    @classmethod
    def full_pattern(cls, pattern):
        return "".join(cls._log_prefix) + str(pattern) + "".join(cls._log_suffix)

    @classmethod
    def warn(cls, pattern, *arg, **kwargs):
        pattern = cls.full_pattern(pattern)
        cls._logger.warn(pattern, *arg, **kwargs)

    @classmethod
    def info(cls, pattern, *arg, **kwargs):
        pattern = cls.full_pattern(pattern)
        cls._logger.info(pattern, *arg, **kwargs)

    @classmethod
    def error(cls, pattern, *arg, **kwargs):
        pattern = cls.full_pattern(pattern)
        cls._logger.error(pattern, *arg, **kwargs)

    @classmethod
    def debug(cls, pattern, *arg, **kwargs):
        pattern = cls.full_pattern(pattern)
        cls._logger.debug(pattern, *arg, **kwargs)

    @classmethod
    def critical(cls, pattern, *arg, **kwargs):
        pattern = cls.full_pattern(pattern)
        cls._logger.critical(pattern, *arg, **kwargs)


TaskExecutor.start_server()


def update_executor():
    try:
        bpy.context.window_manager.bake_tree.tnum = TaskExecutor.process["tnum"]
    except Exception:
        ...
    return 0.1


bpy.app.timers.register(update_executor, persistent=True)


def register():
    ...


def unregister():
    ...
