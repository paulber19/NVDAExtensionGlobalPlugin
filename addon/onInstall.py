# -*- coding: UTF-8 -*-
# onInstall.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2016 - 2022 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import addonHandler
from logHandler import log
import os
import sys
import globalVars
import gui
import winUser

addonHandler.initTranslation()


def checkWindowListAddonInstalled():
	h = winUser.getForegroundWindow()
	addonCheckList = [
		"fakeClipboardAnouncement",
		"listDesFenetres",
		"ListeIconesZoneNotification",
		"DitDossierOuvrirEnregistrer"]
	for addon in addonHandler.getRunningAddons():
		if addon.manifest["name"] in addonCheckList:
			# Translators: message of message box
			msg = _("""Attention, you must uninstall "%s" add-on because it is now included in this add-on""")  # noqa:E501
			gui.messageBox(msg % addon.manifest["name"])
			break
	winUser.setForegroundWindow(h)
