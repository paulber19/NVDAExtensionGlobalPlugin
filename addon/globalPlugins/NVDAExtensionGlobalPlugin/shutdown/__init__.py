#NVDAExtensionGlobalPlugin/shutdown/__init__
#A part of NVDAExtensionGlobalPlugin add-on
#Copyright (C) 2017  paulber19
#This file is covered by the GNU General Public License.


import addonHandler
addonHandler.initTranslation()
from logHandler import log
import time
import wx
import api
import ui
import speech
import gui
import queueHandler
from ..utils.NVDAStrings import NVDAString
from ..utils import isOpened, makeAddonWindowTitle
from gui import nvdaControls
import os
_curAddon = addonHandler.getCodeAddon()
shutdownPath= os.path.join(_curAddon.path, "utilities", "shutdown")
import sys
sys.path.append(shutdownPath)
import shutdown
del sys.path[-1]

class ComputerShutdownDialog(wx.Dialog):
	_delayBeforeShutdownOrRestartLimits = (0, 600)
	_instance = None
	title = None
	
	def __new__(cls, *args, **kwargs):
		if ComputerShutdownDialog._instance is not None:
			return ComputerShutdownDialog._instance
		return wx.Dialog.__new__(cls)

	
	def __init__(self, parent):
		if ComputerShutdownDialog._instance is not None:
			return
		ComputerShutdownDialog._instance = self
		# Translators: This is the title of Computer shutdown dialog window.
		dialogTitle = _("Computer's shut down")
		title = ComputerShutdownDialog.title = makeAddonWindowTitle(dialogTitle)
		super(ComputerShutdownDialog, self).__init__(parent,-1,title)
		self.doGui()
	
	def doGui(self):
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		bHelper= gui.guiHelper.ButtonHelper(wx.HORIZONTAL)
		# Translators: This is a label of a button appearing on Computer shutdown dialog.
		hibernateButton =  bHelper.addButton(self,  label=_("&Hibernate"))
		# Translators: This is a label of a button appearing on Computer shutdowndialog.
		shutdownButton =  bHelper.addButton(self, label=_("&Shutdown"))
		# Translators: This is a label of a button appearing on Computer shutdown  dialog.		
		rebootButton =  bHelper.addButton(self, label=_("&Reboot"))
		sHelper1 = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# Translators: This is the label for a checkbox in the Computer shutdowndialog.
		labelText = _("F&orce running programs to close without warning")
		self.forceOptionBox=sHelper1.addItem (wx.CheckBox(self, label= labelText))
		from ..settings import _addonConfigManager
		self.forceOptionBox.SetValue(_addonConfigManager.getForceCloseOption())
		# Translators: This is a label for a  edit box in Computer shutdown dialog.
		(min, max) = self._delayBeforeShutdownOrRestartLimits
		labelText=_("&Delay befor shutdown or reboot between {min} and {max} seconds").format(min = min, max = max)
		self.delayBeforeShutdownOrRestartBox = sHelper1.addLabeledControl(labelText, nvdaControls.SelectOnFocusSpinCtrl,
			min=int(0),
			max=int(600),
			initial=_addonConfigManager.getdelayBeforeShutdownOrRestart())
		sHelper.addItem(sHelper1)
		sHelper.addItem(bHelper)
		bHelper = sHelper.addDialogDismissButtons(gui.guiHelper.ButtonHelper(wx.HORIZONTAL))
		closeButton= bHelper.addButton(self, id = wx.ID_CLOSE)
		mainSizer.Add(sHelper.sizer, border=gui.guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		# Events
		shutdownButton.Bind(wx.EVT_BUTTON,self.onShutdownButton)
		rebootButton.Bind(wx.EVT_BUTTON,self.onRebootButton)
		hibernateButton.Bind(wx.EVT_BUTTON,self.onhibernateButton)
		closeButton.Bind(wx.EVT_BUTTON, lambda evt: self.Destroy())
		self.SetEscapeId(wx.ID_CLOSE)
	def Destroy(self):
		ComputerShutdownDialog._instance = None
		super(ComputerShutdownDialog, self).Destroy()
	
	def saveSettings(self):
		forceClose = self.forceOptionBox.GetValue()
		timeout = self.delayBeforeShutdownOrRestartBox.GetValue()
		from ..settings import _addonConfigManager
		_addonConfigManager.setForceCloseOption(forceClose)
		_addonConfigManager.setDelayBeforeShutdownOrRestart(timeout)
		_addonConfigManager.saveSettings()
	
	def onShutdownButton(self, event):
		forceClose = self.forceOptionBox.GetValue()
		timeout = self.delayBeforeShutdownOrRestartBox.GetValue()
		shutdown.shutdown(timeout,forceClose)
		self.Close()
	
	def onRebootButton(self, event):
		forceClose = self.forceOptionBox.GetValue()
		timeout = self.delayBeforeShutdownOrRestartBox.GetValue()
		shutdown.reboot(timeout,forceClose)
		self.Close()

	def onhibernateButton(self, evt):
		self.saveSettings()
		self.Close()
		shutdown.suspend(hibernate=True)
	
	@classmethod
	def run(cls):
		if isOpened(cls):
			return
			
		gui.mainFrame.prePopup()		
		d =   cls(gui.mainFrame)
		d.CentreOnScreen()
		d.Show()
		gui.mainFrame.postPopup()		

