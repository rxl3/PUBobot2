# -*- coding: utf-8 -*-
from importlib.machinery import SourceFileLoader
import os
from dotenv import load_dotenv

# http://byatool.com/uncategorized/simple-property-merge-for-python-objects/
def mergeObjectProperties(objectToMergeFrom, objectToMergeTo):
    """
    Used to copy properties from one object to another if there isn't a naming conflict;
    """
    for property in objectToMergeFrom.__dict__:
        #Check to make sure it can't be called... ie a method.
        #Also make sure the objectobjectToMergeTo doesn't have a property of the same name.
        if not callable(objectToMergeFrom.__dict__[property]) and not hasattr(objectToMergeTo, property):
            setattr(objectToMergeTo, property, getattr(objectToMergeFrom, property))

    return objectToMergeTo

# Custom object to hold environment variables (So we don't have to change all the cfg.VAR_NAME to cfg['VAR_NAME'}])
class EnvCfg(object):
	# Takes an os._environ 
	def __init__(self, env: os._Environ):
		for k,v in env.items():
			self.envSetAttr(k, v)

	# Custom function to set the values from .env (which are always string) to list / boolean as needed
	def envSetAttr(self, k: str, v: str):
		if v.isnumeric():
			v = int(v)
		elif v == "[]":
			v = []
		elif v.startswith("[") and v.endswith("]"):
			v = v.strip('[]').split(',')
		elif v in ["True", "true", "TRUE"]:
			v = True
		elif v in ["False", "false", "FALSE"]:
			v = False
		setattr(self, k, v)

# Try load variables from config file, else .env file
print("[CONFIGS] Attempting to load config from config.cfg...")
try:
	cfg = SourceFileLoader('cfg', 'config2.cfg').load_module()
except Exception as e:
	print("[CONFIGS] Failed to load config.cfg! Trying .env instead...")
	try:
		load_dotenv()
		env = os.environ
		cfg = EnvCfg(env)
	except Exception as e2:
		print("[CONFIGS] Failed to load config.cfg and .env file! Throwing Exception and quitting...")
		raise e2
	print("[CONFIGS] Successfully loaded config from .env file!")
else:
	print("[CONFIGS] Successfully loaded config from config.cfg file!")

# set Version
with open('.version', 'r') as f:
	__version__ = f.read()

# test
print(f"[ENV TEST] {cfg.DB_URI}\n")