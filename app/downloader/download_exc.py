import traceback
import functools
import inspect
import logging


logger = logging.getLogger(__name__)


class DownloadError(Exception):
    def __init__(self, msg, tb):
        self.msg_list = [msg]
        self.first_tb = tb

    def update_error(self, msg):
        self.msg_list.append(msg)

    def __str__(self):
        return chr(10).join(self.msg_list[::-1])


def download_error_handling(func, lg=__name__):

    _logger = logging.getLogger(lg)

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        _logger.info(f"Run {self.__class__.__name__}, function: {func.__name__}, {func.__doc__} start")
        try:
            value = func(self, *args, **kwargs)
            _logger.info(f"Run {self.__class__.__name__}, function: {func.__name__}, {func.__doc__} completed")
        except DownloadError as e:
            e.update_error(f"{len(e.msg_list) + 1}. {e.__class__.__name__} when running func: {func.__name__} ({func.__doc__})")
            raise e
        except Exception as e:
            raise DownloadError(msg=f"1. {e.__class__.__name__}: {str(e)} when running func: {func.__name__} ({func.__doc__})", tb=traceback.format_exc())

        return value

    return wrapper


def apply_class_decorator(lg=__name__):

    def decorate(cls):
        for name, fn in inspect.getmembers(cls, inspect.isfunction or inspect.ismethod):
            setattr(cls, name, download_error_handling(fn, lg))
        return cls
    return decorate


class NotAppliedMethod(Exception):
    pass
