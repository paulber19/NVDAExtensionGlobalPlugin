# globalPlugins\NVDAExtensionGlobalPlugin\NVDALogs\__init__.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2017 -2021 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.


import addonHandler
from logHandler import log
import wx
import api
import ui
import gui
import queueHandler
import os
import time
import globalVars
import tempfile
import shutil
from ..utils import makeAddonWindowTitle, getHelpObj
from ..utils.NVDAStrings import NVDAString
from ..utils import contextHelpEx

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
		bHelper = gui.guiHelper.ButtonHelper(wx.HORIZONTAL)
		# Translators: This is a label of a button appearing
		# on NVDA Logs Management Dialog .
		labelText = _("Open &current log")
		openCurrentLogButton = bHelper.addButton(self, label=labelText)
		# Translators: This is a label of a button appearing
		# on NVDA Logs Management Dialog .
		labelText = _("Open &previous log")
		openOldLogButton = bHelper.addButton(self, label=labelText)
		# Translators: This is a label of a button appearing
		# on NVDA Logs Management Dialog .
		labelText = _("Copy current log file &path to clipboard")
		copyCurrentLogPathButton = bHelper.addButton(self, label=labelText)
		# Translators: This is a label of a button appearing
		# on NVDA Logs Management Dialog .
		labelText = _("Copy &old log file path to clipboard")
		copyOldLogPathButton = bHelper.addButton(self, label=labelText)
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
		openCurrentLogButton.Bind(wx.EVT_BUTTON, self.onOpenCurrentLogButton)
		openOldLogButton.Bind(wx.EVT_BUTTON, self.onOpenOldLogButton)
		copyCurrentLogPathButton.Bind(wx.EVT_BUTTON, self.onCopyCurrentLogPathButton)
		copyOldLogPathButton.Bind(wx.EVT_BUTTON, self.onCopyOldLogPathButton)
		closeButton.Bind(wx.EVT_BUTTON, lambda evt: self.Destroy())
		self.SetEscapeId(wx.ID_CLOSE)

	def Destroy(self):
		NVDALogsManagementDialog ._instance = None
		super(NVDALogsManagementDialog, self).Destroy()

	def _openFile(self, oldLog=False):
		if oldLog:
			logFile = os.path.join(os.path.dirname(globalVars.appArgs.logFileName), "nvda-old.log")
			tempLog = "oldNVDALog.txt"
			openErrorMsg = _("Previous log file cannot be opened")
		else:
			logFile = globalVars.appArgs.logFileName
			openErrorMsg = _("Current log file cannot be opened")
			tempLog = "NVDALog.txt"
		if logFile is None or not os.path.exists(logFile):
			wx.CallAfter(
				gui.messageBox,
				# Translators: A message indicating that log cannot be loaded to LogViewer.
				NVDAString("Log is unavailable"),
				# Translators: The title of an error message dialog.
				NVDAString("Error"),
				wx.OK | wx.ICON_ERROR
			)
			return
		tempDir = tempfile.gettempdir()
		file = os.path.join(tempDir, "NVDAExtensionGlobalPlugin-%s" % tempLog)
		shutil.copy(logFile, file)
		time.sleep(0.5)
		count = 1000
		while count:
			if os.path.exists(file):
				break
			time.sleep(0.1)
			count -= 1
		if count == 0:
			log.error("cannot open file: %s" % logFile)
			return
		try:
			os.startfile(file, operation="edit")
		except Exception:
			wx.CallAfter(
				gui.messageBox,
				openErrorMsg,
				_("Open Error"),
				wx.OK | wx.ICON_ERROR)

	def onOpenCurrentLogButton(self, evt):
		self._openFile()
		self.Close()

	def onOpenOldLogButton(self, evt):
		self._openFile(oldLog=True)
		self.Close()

	def onCopyCurrentLogPathButton(self, evt):
		logFile = globalVars.appArgs.logFileName
		if logFile is None or not os.path.exists(logFile):
			wx.CallAfter(
				gui.messageBox,
				# Translators: A message indicating that log cannot be loaded to LogViewer.
				NVDAString("Log is unavailable"),
				# Translators: The title of an error message dialog.
				NVDAString("Error"),
				wx.OK | wx.ICON_ERROR
			)
			return
		if api.copyToClip(logFile):
			ui.message(_("Current log file path copied to clipboard"))
		else:
			ui.message(_("Current log file path cannot be copied to clipboard"))

	def onCopyOldLogPathButton(self, evt):
		logFile = os.path.join(os.path.dirname(globalVars.appArgs.logFileName), "nvda-old.log")
		if logFile is None or not os.path.exists(logFile):
			wx.CallAfter(
				gui.messageBox,
				# Translators: A message indicating that log cannot be loaded to LogViewer.
				NVDAString("Log is unavailable"),
				# Translators: The title of an error message dialog.
				NVDAString("Error"),
				wx.OK | wx.ICON_ERROR
			)
			return
		if api.copyToClip(logFile):
			ui.message(_("old log file path copied to clipboard"))
		else:
			ui.message(_("old log file path cannot be copied to clipboard"))

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
