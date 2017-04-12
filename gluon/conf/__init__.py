from oslo_config import cfg

from gluon.conf import config

CONF = cfg.CONF

config.register_opts(CONF)
