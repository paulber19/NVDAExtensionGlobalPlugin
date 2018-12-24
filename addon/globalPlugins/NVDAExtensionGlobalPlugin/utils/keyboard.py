#NVDAExtensionGlobalPlugin/commandKeysSelectiveAnnouncement/keyboard.py
#A part of NVDAExtensionGlobalPlugin add-on
#Copyright (C) 2016  paulber19
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.

import addonHandler
from logHandler import log
import os.path
from cStringIO import StringIO
import configobj
from validate import Validator
import globalVars
from locale import getdefaultlocale

_configSpec = """
[KeyboardKeys]
	keys = string(default="")
[editionKeyCommands]
	[default]
		copy = string(default = "kb:control+c")
		cut = string(default = "kb:control+x")
		paste = string( default = "kb:control+v")
		undo = string( default = "kb:control+z")
		selectAll = string( default = "kb:control+a")
"""

def getKeyboardKeysIniFilePath():
	from languageHandler import curLang
	langs = [curLang,]
	addonFolderPath = addonHandler.getCodeAddon().path
	lang = curLang
	if '_' in lang:
		langs.append(lang.split("_")[0])
	langs.append("en")
	for lang in langs:
		langDir = os.path.join(addonFolderPath,"locale",lang.encode("utf-8"))
		if os.path.exists(langDir):
			file=os.path.join(langDir,"keyboard.ini")
			if os.path.isfile(file):
				log.debugWarning("keyboard.ini file loaded from locale\\%s folder"%lang)
				return file
	log.error("keyboard.ini file not found")
	return ""

def getKeyboardKeys():
	keys = getKeyboardIniConfig()["KeyboardKeys"]["keys"]
	return list(keys)

def getEditionKeyCommands(obj= None):
	conf = getKeyboardIniConfig()["editionKeyCommands"].copy()
	d = conf["default"].copy()
	if obj is None:
		return d
	appName = obj.appModule.appName
	if appName in conf.keys():
		
		d.update(conf[appName])
	return d

def getKeyboardIniConfig():
	global _conf
	if _conf is not None:
		return _conf
	path = getKeyboardKeysIniFilePath()
	conf = configobj.ConfigObj(path, configspec=StringIO(_configSpec), encoding="utf-8", list_values = False)
	conf.newlines = "\r\n"
	val = Validator()
	ret = conf.validate(val, preserve_errors=True, copy=True)
	if ret != True:
		log.warning("KeyboardKeys configuration file  is invalid: %s", ret)
	_conf = conf
	return conf
# singleton
_conf = None