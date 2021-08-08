# globalPlugins\NVDAExtensionGlobalPlugin\NVDALogs\__init__.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2017 -2021 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.


import addonHandler
import wx
import api
import ui
import gui
import queueHandler
import os
from logHandler import _getDefaultLogFilePath
from ..utils import makeAddonWindowTitle

addonHandler.initTranslation()


class NVDALogsManagementDialog (wx.Dialog):
	_instance = None
	title = None

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
		super(NVDALogsManagementDialog, self).__init__(parent, -1, title)
		self.doGui()

	def doGui(self):
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		bHelper = gui.guiHelper.ButtonHelper(wx.HORIZONTAL)
		# Translators: This is a label of a button appearing
		# on NVDA Logs Management Dialog .
		openCurrentLogButton = bHelper.addButton(self, label=_("Open current &log"))
		# Translators: This is a label of a button appearing
		# on NVDA Logs Management Dialog .
		labelText = _("Open &previous log")
		openOldLogButton = bHelper.addButton(self, label=labelText)
		# Translators: This is a label of a button appearing
		# on NVDA Logs Management Dialog .
		copyCurrentLogPathButton = bHelper.addButton(
			self, label=_("Copy log &path to clipboard"))
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
		closeButton.Bind(wx.EVT_BUTTON, lambda evt: self.Destroy())
		self.SetEscapeId(wx.ID_CLOSE)

	def Destroy(self):
		NVDALogsManagementDialog ._instance = None
		super(NVDALogsManagementDialog, self).Destroy()

	def _openFile(self, logFile, openErrorMsg=""):
		try:
			os.startfile(logFile)
		except:  # noqa:E722
			wx.CallAfter(
				gui.messageBox,
				errorMsg,
				_("Open Error"),
				wx.OK | wx.ICON_ERROR)

	def onOpenCurrentLogButton(self, evt):
		logFile = os.path.join(os.path.dirname(_getDefaultLogFilePath()), "nvda.log")
		openErrorMsg = _("Current log file cannot be opened")
		self._openFile(logFile, openErrorMsg)
		self.Close()

	def onOpenOldLogButton(self, evt):
		logFile = os.path.join(
			os.path.dirname(_getDefaultLogFilePath()),
			"nvda-old.log")
		openErrorMsg = _("Previous log file cannot be opened")
		self._openFile(logFile, openErrorMsg)
		self.Close()

	def onCopyCurrentLogPathButton(self, evt):
		logFile = os.path.join(os.path.dirname(_getDefaultLogFilePath()), "nvda.log")
		if api.copyToClip(logFile):
			ui.message(_("Current log file path copied to clipboard"))
		else:
			ui.message(_("Current log file path cannot be copied to clipboard"))

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
