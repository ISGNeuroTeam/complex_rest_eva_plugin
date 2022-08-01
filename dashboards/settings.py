import configparser
import os

from pathlib import Path
from core.settings.ini_config import merge_ini_config_with_defaults, configparser_to_dict


default_ini_config = {
    'static': {
        'use_nginx': 'True',
        'base_url': 'cache/{}',
        'static_path': '/opt/otp/static/',
    },
    'general':{
        'logs_path': '.',
    },
    'mem_conf':{
        'path': '/opt/otp/caches/'
    }
}



# try to read path to config from environment
conf_path_env = os.environ.get('dashboards_conf', None)
base_dir = Path(__file__).resolve().parent
if conf_path_env is None:
    conf_path = base_dir / 'dashboards.conf'
else:
    conf_path = Path(conf_path_env).resolve()

config = configparser.ConfigParser()

config.read(conf_path)

config = configparser_to_dict(config)

ini_config = merge_ini_config_with_defaults(config, default_ini_config)


STATIC_CONF = ini_config['static']
MEM_CONF = ini_config['mem_conf']
LOGS_PATH = ini_config['general'].get('logs_path', '.')
