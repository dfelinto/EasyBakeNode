import time
from functools import wraps


def timeit(func):
    """
    装饰器，用于测量函数执行时间。
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Function '{func.__name__}' executed in {end_time - start_time:.4f} seconds.")
        return result
    return wrapper


class ScopeTimer:
    def __init__(self, name: str = "", prt=print):
        self.name = name
        self.time_start = time.time()
        self.echo = prt

    def __del__(self):
        self.echo(f"{self.name}: cost {time.time() - self.time_start:.4f}s")


class CtxTimer:
    def __init__(self, name: str = "", prt=print):
        self.name = name
        self.time_start = time.time()
        self.echo = prt

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.echo(f"{self.name}: cost {time.time() - self.time_start:.4f}s")
