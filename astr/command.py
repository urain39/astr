import sys
import json

from pathlib import Path
from .extractor import extract as _extract
from .injector import inject as _inject

_CONST_EXTRACT = 'extract'
_CONST_TRANSLATE = 'translate'
_CONST_INCLUDE = 'include'
_CONST_ENCODING = 'encoding'
_CONST_DIRECTORY = 'directory'

def extract(config):
	inc = config.get(_CONST_EXTRACT, _CONST_INCLUDE)
	enc = config.get(_CONST_EXTRACT, _CONST_ENCODING)
	dir = config.get(_CONST_EXTRACT, _CONST_DIRECTORY)

	cwd = Path('.')
	std = Path(dir)

	new = None
	for i in cwd.glob(inc):
		if i.is_file():
			text = i.read_text(encoding=enc)

			new = (std / (i.name + '.json'))
			new.parent.mkdir(parents=True, exist_ok=True)

			new.write_text(json.dumps(
				_extract(text)
			), encoding='utf-8')

def inject(config):
	pass

def execute(cmd, config):
	if cmd in ('extract', 'x'):
		extract(config)
	elif cmd in ('inject', 'i'):
		inject(config)
	else:
		print(f'Unsupported command \'{cmd}\'')
