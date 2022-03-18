import configparser
import os
from pathlib import Path

from core.settings.ini_config import merge_ini_config_with_defaults
from plugins.db_connector.connector_singleton import db as DB_CONN


default_ini_config = {
    'logging': {
        'level': 'INFO'
    },
    'db_conf': {
        'host': 'localhost',
        'port': '5432',
        'database':  'complex_rest_eva_plugin',
        'user': 'complex_rest_eva_plugin',
        'password': 'complex_rest_eva_plugin'
    }
}

# # # # # #  Configuration section  # # # # # # #

basedir = os.path.dirname(os.path.abspath(__file__))

ot_simple_rest_conf = configparser.ConfigParser()
ot_simple_rest_conf.read(os.path.join(basedir, 'dashboards.conf'))


STATIC_CONF = dict(ot_simple_rest_conf['static'])
MEM_CONF = dict(ot_simple_rest_conf['mem_conf'])
LOGS_PATH = dict(ot_simple_rest_conf['general']).get('logs_path', '.')
config_parser = configparser.ConfigParser()

config_parser.read(Path(__file__).parent / 'dashboards.conf')

ini_config = merge_ini_config_with_defaults(config_parser, default_ini_config)

# configure your own database if you need
# DATABASE = {
#         "ENGINE": 'django.db.backends.postgresql',
#         "NAME": ini_config['db_conf']['database'],
#         "USER": ini_config['db_conf']['user'],
#         "PASSWORD": ini_config['db_conf']['password'],
#         "HOST": ini_config['db_conf']['host'],
#         "PORT": ini_config['db_conf']['port']
# }