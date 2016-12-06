'''
Created on Jan 16, 2016

@author: enikher
'''
import logging
import datetime
import os
import sys

LOG = logging.getLogger(__name__)
LOG_LEVEL = logging.DEBUG
LOG_PATH = "/tmp/%s.log" % os.path.basename(sys.argv[0])
logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                    filename=LOG_PATH,
                    datefmt='%Y-%m-%dT:%H:%M:%s', level=LOG_LEVEL)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
console.setFormatter(formatter)
LOG.addHandler(console)


def log_enter_exit(func):

    def inner(self, *args, **kwargs):
        LOG.debug(("Entering %(cls)s.%(method)s "
                   "args: %(args)s, kwargs: %(kwargs)s") %
                  {'cls': self.__class__.__name__,
                   'method': func.__name__,
                   'args': args,
                   'kwargs': kwargs})
        start = datetime.datetime.now()
        ret = func(self, *args, **kwargs)
        end = datetime.datetime.now()
        LOG.debug(("Exiting %(cls)s.%(method)s. "
                   "Spent %(duration)s sec. "
                   "Return %(return)s") %
                  {'cls': self.__class__.__name__,
                   'duration': end - start,
                   'method': func.__name__,
                   'return': ret})
        return ret
    return inner


def for_all_methods(decorator):
    # @for_all_methods(log_enter_exit)
    # class ...

    def decorate(cls):
        for attr in cls.__dict__:
            if callable(getattr(cls, attr)):
                setattr(cls, attr, decorator(getattr(cls, attr)))
        return cls
    return decorate
