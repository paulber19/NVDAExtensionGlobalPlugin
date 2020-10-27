# coding: utf-8
# state.py
# common Part of all of my add-ons
# Copyright 2019 Paulber19


import addonHandler
from logHandler import log
import os
import time
import pickle
addonHandler.initTranslation()

# delay between update checks
addonUpdateCheckInterval = 86400  # one day
#: Persistent state information.
#: @type: dict
_state = None
_stateFileName = None


#: The time to wait between checks.
addonUpdateCheckInterval = 86400  # one day


def initialize():
	global _state, _stateFilename
	addonPath = addonHandler.getCodeAddon().path
	_stateFilename = os.path.join(addonPath, "updateCheckState.pickle")
	try:
		# 9038: Python 3 requires binary format when working with pickles.
		with open(_stateFilename, "rb") as f:
			_state = pickle.load(f)
	except:  # noqa:E722
		log.debugWarning("update state file don't exist: initialization with default values", exc_info=False)  # noqa:E501
		# Defaults.
		_state = {
			"lastCheck": 0,
			"remindUpdate": False,
		}


def saveState():
	try:
		# #9038: Python 3 requires binary format when working with pickles.
		with open(_stateFilename, "wb") as f:
			pickle.dump(_state, f)
	except:  # noqa:E722
		log.debugWarning("Error saving state", exc_info=True)


def getLastCheck():
	return _state["lastCheck"]


def setLastCheck():
	global _state
	_state["lastCheck"] = time.time()
	_state["remindUpdate"] = False
	saveState()


def setRemindUpdate(on=True):
	global _state
	_state["lastCheck"] = time.time()
	_state["remindUpdate"] = on
	saveState()


def getRemindUpdate():
	return _state["remindUpdate"]
