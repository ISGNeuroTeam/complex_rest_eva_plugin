import configparser
import os
from pathlib import Path
from core.settings.ini_config import merge_ini_config_with_defaults
from psycopg2.pool import ThreadedConnectionPool

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
ot_simple_rest_conf.read(os.path.join(basedir, 'quizs.conf'))

db_conf = dict(ot_simple_rest_conf['db_conf_eva'])
mem_conf = dict(ot_simple_rest_conf['mem_conf'])
disp_conf = dict(ot_simple_rest_conf['dispatcher'])
resolver_conf = dict(ot_simple_rest_conf['resolver'])
static_conf = dict(ot_simple_rest_conf['static'])
user_conf = dict(ot_simple_rest_conf['user'])
pool_conf = dict(ot_simple_rest_conf['db_pool_conf'])

# # # # # # # # # # # # # # # # # # # # # # # # # #

DB_POOL = ThreadedConnectionPool(int(pool_conf['min_size']), int(pool_conf['max_size']), **db_conf)


config_parser = configparser.ConfigParser()

config_parser.read(Path(__file__).parent / 'quizs.conf')

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
