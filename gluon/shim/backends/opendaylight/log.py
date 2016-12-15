#    Copyright 2016, Ericsson AB
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import datetime
import logging
import os
import sys

LOG = logging.getLogger(__name__)
LOG_LEVEL = logging.DEBUG
LOG_PATH = "/tmp/%s.log" % os.path.basename(sys.argv[0])
logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                    filename=LOG_PATH,
                    datefmt='%Y-%m-%dT:%H:%M:%s', level=LOG_LEVEL)
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
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
