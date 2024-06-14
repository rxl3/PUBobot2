# -*- coding: utf-8 -*-
from importlib.machinery import SourceFileLoader
import os
from dotenv import load_dotenv, dotenv_values 

# Load config from .env file instead of config.cfg - probably not the most elegant way to do this but it works?
class Config:
	name="test"

cfg = Config

for x,y in dotenv_values(".env").items():
	if (y=="False"):
		setattr(cfg, x, False)
	elif (y=="True"):
		setattr(cfg, x, True)
	else:
		setattr(cfg, x, y)

# Load config
# try:
# 	cfg = SourceFileLoader('cfg', 'config.cfg').load_module()
# except Exception as e:
# 	print("Failed to load config.cfg file!")
# 	raise e

with open('.version', 'r') as f:
	__version__ = f.read()
