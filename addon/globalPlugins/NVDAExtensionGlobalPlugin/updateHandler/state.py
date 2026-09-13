# coding: utf-8
# state.py
# common Part of all of my add-ons
# Copyright 2019-2026 Paulber19


import addonHandler
from logHandler import log
import os
import time
import yaml

addonHandler.initTranslation()

#: Persistent state information.
#: @type: dict
_state = None
_stateFileName = None

#: The time to wait between checks.
addonUpdateCheckInterval = 86400  # one day


def initialize():
	global _state, _stateFilename
	addonPath = addonHandler.getCodeAddon().path
	try:
		_stateFilename = os.path.join(addonPath, "updateCheckState.yaml")
		with open(_stateFilename, "r") as f:
			_state = yaml.safe_load(f)
	except Exception:
		log.debugWarning("update state file don't exist: initialization with default values", exc_info=False)
		# Defaults.
		_state = {
			"lastCheck": 0,
			"remindUpdate": False,
		}


def saveState():
	try:
		with open(_stateFilename, "w") as f:
			yaml.dump(_state, f, indent=4, sort_keys=False)
	except Exception:
		log.debugWarning("Error saving state", exc_info=True)


def getLastCheck():
	return _state["lastCheck"]


def setLastCheck():
	# global _state
	_state["lastCheck"] = time.time()
	_state["remindUpdate"] = False
	saveState()


def setRemindUpdate(on=True):
	# global _state
	_state["lastCheck"] = time.time()
	_state["remindUpdate"] = on
	saveState()


def getRemindUpdate():
	return _state["remindUpdate"]
