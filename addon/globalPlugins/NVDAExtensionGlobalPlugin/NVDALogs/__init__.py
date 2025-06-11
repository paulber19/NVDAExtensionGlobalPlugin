# globalPlugins\NVDAExtensionGlobalPlugin\NVDALogs\__init__.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2017 - 2025 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.


import addonHandler
from logHandler import log
import wx
import api
import ui
import gui
import queueHandler
import time
import globalVars
import shutil
from ..utils import makeAddonWindowTitle, getHelpObj
from ..utils.NVDAStrings import NVDAString
from ..gui import contextHelpEx
import os
import sys
_curAddon = addonHandler.getCodeAddon()
sharedPath = os.path.join(_curAddon.path, "shared")
sys.path.append(sharedPath)
from messages import alert
del sys.path[-1]
del sys.modules["messages"]


addonHandler.initTranslation()


class NVDALogsManagementDialog (
	contextHelpEx.ContextHelpMixinEx,
	wx.Dialog):
	_instance = None
	title = None
	# help in the user manual.
	helpObj = getHelpObj("hdr9")

	def __new__(cls, *args, **kwargs):
		if NVDALogsManagementDialog ._instance is not None:
			return NVDALogsManagementDialog ._instance
		return wx.Dialog.__new__(cls)

	def __init__(self, parent):
		if NVDALogsManagementDialog ._instance is not None:
			return
		NVDALogsManagementDialog ._instance = self
		# Translators: This is the title of the NVDA Logs Management Dialog .
		dialogTitle = _("NVDA logs management")
		title = NVDALogsManagementDialog .title = makeAddonWindowTitle(dialogTitle)
		super(NVDALogsManagementDialog, self).__init__(
			parent,
			-1,
			title,
			style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX
		)
		self.doGui()

	def doGui(self):
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# Translators: This is the label for a choice box in the NVDA Logs Management Dialog .
		labelText = _("NVDA &log:")
		self.NVDALogChoiceBox = sHelper.addLabeledControl(
			labelText, wx.Choice, choices=[_("Current"), _("Previous")])
		self.NVDALogChoiceBox.SetSelection(0)
		bHelper = gui.guiHelper.ButtonHelper(wx.HORIZONTAL)
		# Translators: This is a label of a button appearing
		# on NVDA Logs Management Dialog .
		labelText = _("&Open the log")
		openLogButton = bHelper.addButton(self, label=labelText)
		openLogButton .SetDefault()
		# Translators: This is a label of a button appearing
		# on NVDA Logs Management Dialog .
		labelText = _("Copy log file &path to clipboard")
		copyLogPathButton = bHelper.addButton(self, label=labelText)
		sHelper.addItem(bHelper)
		bHelper = sHelper.addDialogDismissButtons(
			gui.guiHelper.ButtonHelper(wx.HORIZONTAL))
		closeButton = bHelper.addButton(self, id=wx.ID_CLOSE)
		mainSizer.Add(
			sHelper.sizer,
			border=gui.guiHelper.BORDER_FOR_DIALOGS,
			flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		# events
		openLogButton.Bind(wx.EVT_BUTTON, self.onOpenLogButton)
		copyLogPathButton.Bind(wx.EVT_BUTTON, self.onCopyLogPathButton)
		closeButton.Bind(wx.EVT_BUTTON, lambda evt: self.Destroy())
		self.SetEscapeId(wx.ID_CLOSE)

	def Destroy(self):
		NVDALogsManagementDialog ._instance = None
		super(NVDALogsManagementDialog, self).Destroy()

	def _openFile(self, oldLog=False):
		nvdaLogPath = os.path.dirname(globalVars.appArgs.logFileName)
		if oldLog:
			logFile = os.path.join(nvdaLogPath, r"nvda-old.log")
			tempLog = "oldNVDALog.txt"
			openErrorMsg = _("Previous log file cannot be opened")
		else:
			logFile = globalVars.appArgs.logFileName
			openErrorMsg = _("Current log file cannot be opened")
			tempLog = "NVDALog.txt"
		if logFile is None or not os.path.exists(logFile):

			wx.CallAfter(
				alert,
				# Translators: A message indicating that log cannot be loaded to LogViewer.
				NVDAString("Log is unavailable"),
				# Translators: The title of an error message dialog.
				NVDAString("Error"),
			)
			return

		tempFile = os.path.join(nvdaLogPath, r"NVDAExtensionGlobalPlugin-%s" % tempLog)
		shutil.copy(logFile, tempFile)
		time.sleep(0.5)
		count = 1000
		while count:
			if os.path.exists(tempFile):
				break
			time.sleep(0.1)
			count -= 1
		if count == 0:
			log.error("cannot open file: %s" % logFile)
			return
		try:
			os.startfile(tempFile, operation="edit")
			return
		except Exception:
			import shellapi
			from winUser import SW_SHOWNORMAL
			shellapi.ShellExecute(
				hwnd=None,
				operation="open",
				file="notepad.exe", parameters=tempFile, directory=nvdaLogPath, showCmd=SW_SHOWNORMAL,)
			return

			wx.CallAfter(
				alert,
				openErrorMsg,
				_("Open Error"),
			)

	def onOpenLogButton(self, evt):
		if self.NVDALogChoiceBox .GetSelection() == 0:
			# open current log
			self._openFile()
		else:
			# open old log
			self._openFile(oldLog=True)
		self.Close()

	def onCopyLogPathButton(self, evt):
		currentLog = True if self.NVDALogChoiceBox .GetSelection() == 0 else False
		if currentLog:
			logFile = globalVars.appArgs.logFileName
		else:
			logFile = os.path.join(os.path.dirname(globalVars.appArgs.logFileName), "nvda-old.log")
		if logFile is None or not os.path.exists(logFile):
			wx.CallAfter(
				alert,
				# Translators: A message indicating that log cannot be loaded to LogViewer.
				NVDAString("Log is unavailable"),
				# Translators: The title of an error message dialog.
				NVDAString("Error"),
			)
			return
		if api.copyToClip(logFile):
			print("passe")
			if currentLog:
				ui.message(_("Current log file path copied to clipboard"))
			else:
				ui.message(_("Old log file path copied to clipboard"))
		else:
			if currentLog:
				ui.message(_("Current log file path cannot be copied to clipboard"))
			else:
				ui.message(_("Old log file path cannot be copied to clipboard"))

	@classmethod
	def run(cls):
		if cls._instance is not None:
			msg = _("%s dialog is allready open") % cls.title
			queueHandler.queueFunction(
				queueHandler.eventQueue, ui.message, msg)
			return
		gui.mainFrame.prePopup()
		d = cls(gui.mainFrame)
		d.CentreOnScreen()
		d.ShowModal()
		gui.mainFrame.postPopup()
