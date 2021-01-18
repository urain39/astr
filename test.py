from configparser import ConfigParser
from astr.command import execute

cfg = ConfigParser()
cfg.read('astr.ini', encoding='utf-8')

execute('x', cfg)
