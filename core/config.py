# -*- coding: utf-8 -*-
from importlib.machinery import SourceFileLoader
import os
from os.path import join, dirname
from dotenv import load_dotenv

# Custom object to hold environment variables (So we don't have to change all the cfg.VAR_NAME to cfg['VAR_NAME'}])
class EnvCfg(object):
	# Takes an os._environ 
	def __init__(self, env: os._Environ):
		for k,v in env.items():
			self.envSetAttr(k, v)

	# Custom function to set the values from .env (which are always string) to list / boolean as needed
	def envSetAttr(self, k: str, v: str):
		if v.startswith("[") and v.endswith("]"):
			v = v.strip('[]').split(',')
		elif v in ["True", "true", "TRUE"]:
			v = True
		elif v in ["False", "false", "FALSE"]:
			v = False
		setattr(self, k, v)

# Try load variables from config file, else .env file
print("\n[CONFIGS]Attempting to load config from config.cfg...")
try:
	cfg = SourceFileLoader('cfg', 'config2.cfg').load_module()
except Exception as e:
	print("[CONFIGS]Failed to load config.cfg! Trying .env instead...")
	try:
		load_dotenv()
		env = os.environ
		cfg = EnvCfg(env)
	except Exception as e2:
		print("[CONFIGS]Failed to load config.cfg and .env file! Throwing Exception and quitting...")
		raise e2
	print("[CONFIGS]Successfully loaded config from .env file!\n")
else:
	print("[CONFIGS]Successfully loaded config from config.cfg file!\n")

# set Version
with open('.version', 'r') as f:
	__version__ = f.read()
