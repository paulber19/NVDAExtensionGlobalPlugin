# globalPlugins\NVDAExtensionGlobalPlugin\utils\contextHelpEx.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2021-2023 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import os
import tempfile
import typing
import wx
from logHandler import log
from .secure import inSecureMode
from documentationUtils import getDocFilePath


# same as contextHelp of NVDA core
# but for also addon user documentation


def writeRedirect(helpId: str, helpFilePath: str, contextHelpPath: str):
	redirect = rf"""
<html><head>
<meta http-equiv="refresh" content="0;url=file:///{helpFilePath}#{helpId}" />
</head></html>
	"""
	with open(contextHelpPath, 'w') as f:
		f.write(redirect)


def showHelp(helpObj):
	"""Display the corresponding section of the user guide when either the Help
	button in an NVDA dialog is pressed or the F1 key is pressed on a
	recognized control.
	"""

	import ui
	import queueHandler
	if not helpObj:
		# Translators: Message indicating no context sensitive help is available for the control or dialog.
		noHelpMessage = _("No help available here.")
		queueHandler.queueFunction(queueHandler.eventQueue, ui.message, noHelpMessage)
		return
	if isinstance(helpObj, str):
		# for NVDA
		helpId = helpObj
		helpFile = getDocFilePath("userGuide.html")
	elif isinstance(helpObj, tuple):
		# for add-ons
		(helpId, helpFile) = helpObj
	else:
		# erreur
		log.error("helpObj is invalid: %s" % type(helpObj))
		return
	if helpFile is None or not os.path.exists(helpFile) or not os.path.isfile(helpFile):
		# Translators: Message shown when trying to display context sensitive help,
		# indicating that	the user guide could not be found.
		noHelpMessage = _("No user guide found.")
		log.debugWarning("No user guide found: possible cause - running from source without building user docs")
		queueHandler.queueFunction(queueHandler.eventQueue, ui.message, noHelpMessage)
		return
	log.debug(f"Opening help: helpId = {helpId}, userGuidePath: {helpFile}")
	nvdaTempDir = os.path.join(tempfile.gettempdir(), "nvda")
	if not os.path.exists(nvdaTempDir):
		os.mkdir(nvdaTempDir)
	contextHelpRedirect = os.path.join(nvdaTempDir, "contextHelp.html")
	try:
		# a redirect is necessary because not all browsers support opening a fragment URL from the command line.
		writeRedirect(helpId, helpFile, contextHelpRedirect)
	except Exception:
		log.error("Unable to write context help redirect file.", exc_info=True)
		return
	try:
		log.warning("open help file: %s, %s" % (helpId, helpFile))
		queueHandler.queueFunction(queueHandler.eventQueue, ui.message, _("Please wait"))
		os.startfile(f"file://{contextHelpRedirect}")
	except Exception:
		log.error("Unable to launch context help.", exc_info=True)


def bindHelpEvent(helpObj, window: wx.Window):
	window.Unbind(wx.EVT_HELP)
	window.Bind(
		wx.EVT_HELP,
		lambda evt: _onEvtHelp(helpObj, evt),
	)
	log.debug(f"Did context help binding for {window.__class__.__qualname__}")


def _onEvtHelp(helpObj, evt: wx.HelpEvent):
	if inSecureMode():
		# Disable context help in secure screens to avoid opening a browser with system-wide privileges.
		return
	# Don't call evt.skip. Events bubble upwards through parent controls.
	# Context help for more specific controls should override the less specific parent controls.
	showHelp(helpObj)


class ContextHelpMixinEx():

	#: The name of the appropriate anchor in NVDA help that provides help for the wx.Window this mixin is
	# used with.
	helpId = ""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		helpId = getattr(self, "helpId", None)
		# for add-ons
		helpObj = getattr(self, "helpObj", None)
		if helpId is None or not isinstance(helpId, str):
			log.warning(f"No helpId (or incorrect type) for: {self.__class__.__qualname__} helpId: {helpId!r}")
			helpId = ""
		window = typing.cast(wx.Window, self)
		if helpObj is not None and isinstance(helpObj, tuple):
			bindHelpEvent(helpObj, window)
		else:
			bindHelpEvent(helpId, window)

	def bindHelpEvent(self, helpObj, window: wx.Window):
		"""A helper method, to bind helpId strings to sub-controls of this Window.
		Useful for adding context help to wx controls directly.
		helpObj is even a string(for NVDA) ora tuple (for add-ons)
		"""
		bindHelpEvent(helpObj, window)
