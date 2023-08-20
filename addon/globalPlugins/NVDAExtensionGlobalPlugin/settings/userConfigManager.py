# globalPlugins\NVDAExtensionGlobalPlugin\settings\configsSwitchingDialog.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2021-2023 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.


import addonHandler
from logHandler import log
import globalVars
import config
import os
import sys
import os.path
import eventHandler
import queueHandler
import api
import time
import speech
import ui
import wx
import gui
from gui import nvdaControls
import shutil
from configobj import ConfigObj
from configobj.validate import Validator, VdtTypeError
from io import StringIO
from versionInfo import version_year, version_major
from ..utils import makeAddonWindowTitle, isOpened, getHelpObj
from ..utils.secure import inSecureMode
from ..utils.NVDAStrings import NVDAString
from ..utils import contextHelpEx


addonHandler.initTranslation()
NVDAVersion = [version_year, version_major]

_configSpec = ""
# section Ids
SCT_UserConfigurations = "UserConfigurations"

# id for the location path of each configuration name
ID_Path = "path"

_lastSelectedUserConfigLocation = None


class UserConfigurationsManager(object):
	def __init__(self):

		self.curAddon = addonHandler.getCodeAddon()
		self.addonName = self.curAddon.manifest["name"]
		self.activeUserConfigPath = self.getActiveConfigurationPath()
		self.load()
		self.addUserConfig(self.activeUserConfigPath)
		config.post_configSave.register(self.handlePostConfigSave)

	def getUserConfigParentFolder(self):
		import globalVars
		userConfigPath = globalVars.appArgs.configPath
		return os.path.split(userConfigPath)[0]

	def load(self):
		curAddon = addonHandler.getCodeAddon()
		addonName = curAddon.manifest['name']
		path = os.path.join(self.getUserConfigParentFolder(), "%s-userConfigs.ini" % addonName)
		if not os.path.exists(path):
			# no userConfiguration profile
			conf = ConfigObj(
				"",
				configspec=StringIO(_configSpec),
				default_encoding='utf8',
				encoding="utf-8",
				list_values=False)
			conf.filename = path
		else:
			conf = ConfigObj(
				path,
				configspec=StringIO(_configSpec),
				default_encoding='utf8',
				encoding="utf-8",
				list_values=False)
		conf.newlines = "\r\n"
		val = Validator()
		res = conf.validate(val, preserve_errors=True, copy=True)
		if not res:
			log.error("userConfigprofiles ini file invalid: %s" % res)
			return
		self.conf = conf

	def save(self):
		# We never want to save config if runing securely
		if inSecureMode():
			return
		val = Validator()
		try:
			self.conf.validate(val, copy=True)
		except VdtTypeError:
			# error in userConfigprofiles configuration
			log.error("UserConfigprofiles configuration: validator error: %s" % self.addonConfig.errors)
			return
		try:
			self.conf.write()
			log.warning("UserConfigurationsManager: userConfigprofiles configuration saved")
		except Exception:
			log.warning(
				"UserConfigurationsManager: Could not save userConfigprofiles configuration "
				"- probably read only file system: %s" % self.conf.filename)

	def handlePostConfigSave(self):
		self.save()

	def addUserConfig(self, userConfigFolderPath):
		path = os.path.abspath(os.path.dirname(userConfigFolderPath))
		folderName = os.path.basename(userConfigFolderPath)
		sct = SCT_UserConfigurations
		if sct not in self.conf:
			self.conf[sct] = {}
		if path in self.conf[sct] and folderName in self.conf[sct]:
			# allready exist, so do nothing
			return
		if path not in self.conf[sct]:
			self.conf[sct][path] = {}
		if folderName in ["userConfig", "nvda"]:
			self.conf[sct][path][folderName] = True
		else:
			self.conf[SCT_UserConfigurations][path][folderName] = False

	def deleteUserConfig(self, userConfigFolderPath):
		folderName = os.path.basename(userConfigFolderPath)
		try:
			del self.conf[SCT_UserConfigurations][folderName]
		except Exception:
			pass

	def checkConfigurations(self, conf):
		from copy import deepcopy
		tempConf = deepcopy(conf)
		for path in tempConf:
			for userConfig in tempConf[path]:
				if not os.path.exists(os.path.join(path, userConfig)):
					del conf[path][userConfig]
					if len(conf[path]) == 0:
						del conf[path]
		return conf

	def getUserConfigurations(self):
		if SCT_UserConfigurations not in self.conf:
			return {}
		conf = self.conf[SCT_UserConfigurations].dict()
		conf = self.checkConfigurations(conf)
		return conf

	def setUserConfigurations(self, userConfigs):
		if SCT_UserConfigurations not in self.conf:
			self.conf[SCT_UserConfigurations] = {}
		self.conf[SCT_UserConfigurations] = userConfigs

	def getLastSelectedUserConfigLocation(self):
		path = _lastSelectedUserConfigLocation
		if path is None:
			path = os.path.dirname(_UserConfigurationsManager.activeUserConfigPath)
		return path

	def setLastSelectedUserConfigLocation(self, location):
		global _lastSelectedUserConfigLocation
		_lastSelectedUserConfigLocation = location

	def getUserConfigFolderName(self, userConfigId):
		userConfigFolderName = "nvdaUserConfig-%s" % userConfigId
		return userConfigFolderName

	def deleteUserConfigFolder(self, path):
		if not os.path.isdir(path):
			return
		shutil.rmtree(path, ignore_errors=True)
		if os.path.isdir(path):
			log.warning("Error: the %s folder cannot be deleted" % path)
			# Translators: message to user to report error on folder deletion
			ui.message(_("""Error: the "%s" folder cannot be deleted""") % path)
			return
		log.warning("%s user config folder has been deleted" % path)

	def getActiveConfigurationPath(self):
		import globalVars
		try:
			# configPath is guaranteed to be correct for NVDA, however it will not exist for NVDA_slave.
			# path = os.path.abspath(globalVars.appArgs.configPath)
			path = globalVars.appArgs.configPath
		except AttributeError:
			path = config.getUserDefaultConfigPath()
		return path


# code from nvda core.py  modified to restart nvda with a config-path option

import languageHandler
from core import triggerNVDAExit, NewNVDAInstance


def restart(disableAddons=False, debugLogging=False, configPath=None, secureMode=False):
	"""Restarts NVDA by starting a new copy."""
	if globalVars.appArgs.launcher:
		globalVars.exitCode = 3
		if not triggerNVDAExit():
			log.error("NVDA already in process of exiting, this indicates a logic error.")
		return
	import subprocess
	paramsToRemove = ("--disable-addons", "--debug-logging", "--ease-of-access", "--secure")
	if configPath is not None:
		paramsToRemove += ("--config-path",)
	if NVDAVersion >= [2022, 1]:
		paramsToRemove += languageHandler.getLanguageCliArgs()
	for paramToRemove in paramsToRemove:
		for p in sys.argv:
			if p.startswith(paramToRemove):
				sys.argv.remove(p)
	options = []
	if not hasattr(sys, "frozen"):
		options.append(os.path.basename(sys.argv[0]))
	if disableAddons:
		options.append('--disable-addons')
	if debugLogging:
		options.append('--debug-logging')
	if configPath:
		options.append('--config-path=%s' % configPath)
	if secureMode:
		options.append('--secure')
	if not triggerNVDAExit(NewNVDAInstance(
		sys.executable,
		subprocess.list2cmdline(options + sys.argv[1:]),
		globalVars.appDir
	)):
		log.error("NVDA already in process of exiting, this indicates a logic error.")
	log.warning("restarting NVDA: %s, options: %s" % (
		sys.executable, subprocess.list2cmdline(options + sys.argv[1:])))


class UserConfigManagementDialog(
	contextHelpEx.ContextHelpMixinEx,
	wx.Dialog):
	_instance = None
	title = None
	helpObj = getHelpObj("hdr30")

	def __new__(cls, *args, **kwargs):
		if UserConfigManagementDialog._instance is not None:
			return UserConfigManagementDialog._instance
		return wx.Dialog.__new__(cls)

	def __init__(self, parent):
		if UserConfigManagementDialog._instance is not None:
			return UserConfigManagementDialog._instance
		UserConfigManagementDialog._instance = self
		# Translators: This is the title of the user configuration management dialog.
		dialogTitle = _("User Configurations's management")
		UserConfigManagementDialog.title = makeAddonWindowTitle(dialogTitle)
		super(
			UserConfigManagementDialog, self).__init__(
			parent,
			wx.ID_ANY,
			self.title,
			style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX
		)
		self.userConfigs = _UserConfigurationsManager .getUserConfigurations()
		self.doGui()

	def doGui(self):
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# Translators: This is the label of list box appearing
		# in the User configuration management dialog.
		labelText = _("Configuration's &folders:")
		self.configurationsListBox = sHelper.addLabeledControl(
			labelText,
			wx.ListBox,
			choices=[],
		)
		self.configurationsListBox .Bind(wx.EVT_LISTBOX, self.onSelectFolder)
		self.bindHelpEvent(getHelpObj("hdr30-1"), self.configurationsListBox)
		# the buttons
		bHelper = gui.guiHelper.ButtonHelper(orientation=wx.HORIZONTAL)
		# translators: this is a label for a button
		# in the User configuration management dialog.
		labelText = _("&Restart NVDA with this configuration's folder")
		restartNVDAButton = bHelper.addButton(self, label=labelText)
		restartNVDAButton.Bind(wx.EVT_BUTTON, self.onRestartNVDAButton)
		restartNVDAButton.SetDefault()
		self.bindHelpEvent(getHelpObj("hdr30-1-4"), restartNVDAButton)
		# translators: this is a label for a button
		# in the User configuration management dialog.
		labelText = _("&Prepare this folder")
		self.updateButton = bHelper.addButton(self, label=labelText)
		self.bindHelpEvent(getHelpObj("hdr30-1-3"), self.updateButton)
		# translators: this is a label for a button
		# in the User configuration management dialog.
		labelText = _("&Delete this folder")
		self.deleteButton = bHelper.addButton(self, label=labelText)
		self.deleteButton .Bind(wx.EVT_BUTTON, self.onDeleteButton)
		self.bindHelpEvent(getHelpObj("hdr30-1-2"), self.deleteButton)
		# translators: this is a label for a button
		# in the User configuration management dialog.
		labelText = _("Empt&y this folder")
		self.emptyFolderButton = bHelper.addButton(self, label=labelText)
		self.emptyFolderButton .Bind(wx.EVT_BUTTON, self.onEmptyFolderButton)
		# translators: this is a label for a button
		# in the User configuration management dialog.
		labelText = _("E&xplore this folder")
		self.exploreButton = bHelper.addButton(self, label=labelText)
		self.exploreButton .Bind(wx.EVT_BUTTON, self.onExploreButton)
		self.bindHelpEvent(getHelpObj("hdr30-1-5"), self.exploreButton)
		sHelper.addItem(bHelper)
		bHelper = gui.guiHelper.ButtonHelper(orientation=wx.HORIZONTAL)
		# translators: this is a label for a button
		# in the User configuration management dialog.
		labelText = _("Add &new folder")
		newUserConfigButton = bHelper.addButton(self, label=labelText)
		newUserConfigButton .Bind(wx.EVT_BUTTON, self.onNewUserConfigButton)
		self.bindHelpEvent(getHelpObj("hdr30-1-1"), newUserConfigButton)
		# translators: this is a label for a button
		# in the User configuration management dialog.
		labelText = _("Add &existing folder")
		addUserConfigButton = bHelper.addButton(self, label=labelText)
		addUserConfigButton .Bind(wx.EVT_BUTTON, self.onAddExistingUserConfigButton)
		self.bindHelpEvent(getHelpObj("hdr30-1-1"), addUserConfigButton)
		sHelper.addItem(bHelper)
		bHelper = sHelper.addDialogDismissButtons(
			gui.guiHelper.ButtonHelper(wx.HORIZONTAL))
		closeButton = bHelper.addButton(
			self, id=wx.ID_CLOSE, label=NVDAString("&Close"))
		closeButton.Bind(wx.EVT_BUTTON, self.onCloseButton)
		self.SetEscapeId(wx.ID_CLOSE)
		mainSizer.Add(
			sHelper.sizer, border=gui.guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		self.updateConfigurations()
		# select active configuration folder
		for path in self.configurations:
			if path == _UserConfigurationsManager.activeUserConfigPath:
				index = self.configurations.index(path)
				self.configurationsListBox .SetSelection(index)
		self.configurationsListBox .SetFocus()
		self.onSelectFolder(None)

	def Destroy(self):
		UserConfigManagementDialog._instance = None
		super(UserConfigManagementDialog, self).Destroy()

	def updateButtons(self):
		index = self.configurationsListBox .GetSelection()
		path = self.configurations[index]
		if self.isNVDAUserConfigurationFolder(path):
			# change the update button label to "modify"
			# Translators:  label of  modify button
			# in user configuration management dialog.
			labelText = _("&Modify this folder")
			self.updateButton.Bind(wx.EVT_BUTTON, self.onModifyButton)
		else:
			# change label button to "Prepare")
			# Translators:  label of  prepare button
			# in user configuration management dialog.
			labelText = _("&Prepare this folder")
			self.updateButton.Bind(wx.EVT_BUTTON, self.onPrepareButton)
		self.updateButton.SetLabel(labelText)
		# disable button if there is no other user configuration
		if len(self.configurations) <= 1:
			self.updateButton.Disable()
		else:
			self.updateButton.Enable()
		if path == _UserConfigurationsManager.activeUserConfigPath:
			# disable deleteButton and emptyFolder button
			self.deleteButton .Disable()
			self.emptyFolderButton .Disable()
		else:
			# enable deleteButton and emptyFolder button
			self.deleteButton .Enable()
			self.emptyFolderButton .Enable()
		if os.path.isdir(path):
			self.exploreButton.Enable()
		else:
			self.exploreButton.Disable()

	def onSelectFolder(self, evt):
		self.updateButtons()
		index = self.configurationsListBox .GetSelection()
		path = self.configurations[index]
		if path == _UserConfigurationsManager.activeUserConfigPath:
			# Translators: message to user to report
			# that the selected user configuration folder   is the current active configuration.
			wx.CallLater(100, ui.message, _("Active configuration"))

	def isNVDAUserConfigurationFolder(self, path):
		if os.path.isdir(path):
			dirs = os.listdir(path)
			if "addons" in dirs\
				and "profiles" in dirs\
				and "speechDicts" in dirs\
				and "updates" in dirs\
				and "nvda.ini" in dirs:
				return True
		return False

	def updateConfigurations(self):
		index = self.configurationsListBox .GetSelection()
		self.configurations = []
		for dir in self.userConfigs:
			for folderName in self.userConfigs[dir]:
				path = os.path.join(dir, folderName)
				if os.path.exists(path):
					self.configurations.append(path)
		tempList = []
		for path in self.configurations:
			pre = ""
			if not self.isNVDAUserConfigurationFolder(path):
				pre += "?"
			if path == _UserConfigurationsManager.activeUserConfigPath:
				# add checked symbol before folder name
				pre = chr(0x2713) + pre
			folderName = os.path.basename(path)
			dir = os.path.dirname(path)
			label = "%s %s (%s)" % (pre, folderName, dir)
			tempList.append(label)
		self.configurationsListBox .Clear()
		self.configurationsListBox .AppendItems(tempList)
		if index >= 0:
			self.configurationsListBox .SetSelection(index)
		self.updateButtons()

	def onRestartNVDAButton(self, evt):
		index = self.configurationsListBox .GetSelection()
		path = self.configurations[index]
		if gui.messageBox(
			# Translators: message to confirm nvda restarting with this configuration.
			_("Do you really want to restart NVDA with this user configuration's folder: %s?") % path,
			# Translators: dialog title.
			_("Confirmation"),
			wx.YES | wx.NO) != wx.YES:
			return

		queueHandler.queueFunction(queueHandler.eventQueue, restart, configPath=path)
		self.Close()

	def addUserConfig(self, userConfigFolderPath):
		dir = os.path.dirname(userConfigFolderPath)
		folderName = os.path.basename(userConfigFolderPath)
		if dir not in self.userConfigs:
			self.userConfigs[dir] = {}
		if folderName in ["userConfig", "nvda"]:
			self.userConfigs[dir][folderName] = True
		else:
			self.userConfigs[dir][folderName] = False

	def deleteUserConfig(self, userConfigFolderPath):
		dir = os.path.dirname(userConfigFolderPath)
		folderName = os.path.basename(userConfigFolderPath)
		if dir in self.userConfigs and folderName in self.userConfigs[dir]:
			del self.userConfigs[dir][folderName]
			if len(self.userConfigs[dir]) == 0:
				del self.userConfigs[dir]
			return True
		return False

	def onPrepareButton(self, evt):
		obj = self.FindFocus()
		index = self.configurationsListBox .GetSelection()
		path = self.configurations[index]
		dlg = PrepareFolderDialog(self, path)
		dlg.ShowModal()
		dlg.Destroy()
		self.updateConfigurations()
		self.configurationsListBox .SetSelection(index)
		obj.SetFocus()
		wx.CallAfter(speech.cancelSpeech)

	def onModifyButton(self, evt):
		obj = self.FindFocus()
		index = self.configurationsListBox .GetSelection()
		path = self.configurations[index]
		if path == _UserConfigurationsManager.activeUserConfigPath:
			if gui.messageBox(
				# Translators: message to ask user to continue.
				_("You are going to modify the active configuration's folder. Do you want to continue?"),
				# Translators: message box title .
				_("Warning"),
				wx.YES | wx.NO | wx.CANCEL | wx.NO_DEFAULT) != wx.YES:
				return
		dlg = ModifyFolderDialog(self, path)
		dlg.ShowModal()
		dlg.Destroy()
		self.configurationsListBox .SetSelection(index)
		self.updateConfigurations()
		obj.SetFocus()
		wx.CallAfter(speech.cancelSpeech)

	def onNewUserConfigButton(self, evt):
		focus = self.FindFocus()
		with NewUserConfigurationAddingDialog(self) as dlg:
			if not dlg.ShowModal():
				focus.SetFocus()
				wx.CallAfter(speech.cancelSpeech)
				return
			newFolderPath = dlg.newUserConfigFolderPath
		try:
			os.makedirs(newFolderPath)
		except OSError:
			if not os.path.exists(newFolderPath):
				log.error("Impossible to create the folder: %s" % newFolderPath)
				# Translators: message to user to report error on creation folder.
				ui.message(_("Impossible to create %s folder") % newFolderPath)
				return
		self.addUserConfig(newFolderPath)
		self.updateConfigurations()
		self.configurationsListBox .SetSelection(self.configurations.index(newFolderPath))
		self.updateConfigurations()
		focus.SetFocus()
		wx.CallLater(20, speech.cancelSpeech)
		wx.CallLater(30, self.configurationsListBox .SetFocus)

	def onAddExistingUserConfigButton(self, evt):
		focus = self.FindFocus()
		with ExistingUserConfigurationAddingDialog(self) as dlg:
			if not dlg.ShowModal():
				focus.SetFocus()
				wx.CallAfter(speech.cancelSpeech)
				return
			newUserConfigFolderPath = dlg.newUserConfigFolderPath
		self.addUserConfig(newUserConfigFolderPath)
		self.updateConfigurations()

		self.configurationsListBox .SetSelection(self.configurations.index(newUserConfigFolderPath))
		self.updateConfigurations()
		focus.SetFocus()
		wx.CallLater(20, speech.cancelSpeech)
		wx.CallLater(30, self.configurationsListBox .SetFocus)

	def onDeleteButton(self, evt):
		index = self.configurationsListBox .GetSelection()
		if index < 0:
			# no selection
			return
		focus = self.FindFocus()
		path = self.configurations[index]
		if path == _UserConfigurationsManager.activeUserConfigPath:
			# Translators: message to user to say that active configuration path cannot be deleted.
			ui.message(_("Active configuration path cannot be deleted"))
			return
		if gui.messageBox(
			# Translators: message to confirm folder deletion.
			_("""Do you really want to delete the "%s" folder?""") % os.path.basename(path),
			# Translators: dialog title.
			_("Confirmation"),
			wx.YES | wx.NO | wx.CANCEL | wx.YES_DEFAULT) != wx.YES:
			focus.SetFocus()
			return
		if not self.deleteUserConfig(path):
			return
		if index:
			prevSelectedString = self.configurationsListBox .GetString(index - 1)
		if self.configurationsListBox .Count:
			if index:
				self.configurationsListBox .SetStringSelection(prevSelectedString)
			else:
				self.configurationsListBox .SetSelection(0)
		self.updateConfigurations()
		if os.path.isdir(path):
			shutil.rmtree(path)
		focus.SetFocus()
		wx.CallLater(20, speech.cancelSpeech)
		wx.CallLater(30, self.configurationsListBox .SetFocus)

	def onEmptyFolderButton(self, evt):
		index = self.configurationsListBox .GetSelection()
		if index < 0:
			# no selection
			return
		userConfigPath = self.configurations[index]
		dirs = os.listdir(userConfigPath)
		if len(dirs) == 0:
			# Translators: message to user to report that the folder is emppty.
			ui.message(_("The folder %s is already empty") % os.path.basename(userConfigPath))
			return
		if gui.messageBox(
			# Translators: message to user to confirm the dump of the folder.
			_("""Do you really want to delete all the content of the "%s" folder?""") % (
				os.path.basename(userConfigPath)),
			# Translators: dialog title.
			_("Confirmation"),
			wx.YES | wx.NO | wx.CANCEL | wx.YES_DEFAULT) != wx.YES:
			return
		api.processPendingEvents()
		time.sleep(0.5)
		speech.cancelSpeech()

		def callback(userConfigPath, dirs):
			# Translators: message to user to wait.
			speech.speakMessage(_("Please wait"))
			from ..utils import runInThread
			th = runInThread.RepeatBeep(
				delay=2.0, beep=(200, 200))
			th.start()
			for item in dirs:
				path = os.path.join(userConfigPath, item)
				if os.path.isdir(path):
					shutil.rmtree(path)
				else:
					os.remove(path)
			th.stop()
			del th
			self.updateConfigurations()
			# Translators: message to user to report end of deletion.
			ui.message(_("End of deletion"))
			obj = api.getFocusObject()
			eventHandler.queueEvent("gainFocus", obj)

		wx.CallLater(100, callback, userConfigPath, dirs)

	def onExploreButton(self, evt):
		index = self.configurationsListBox .GetSelection()
		path = self.configurations[index]
		import subprocess
		windir = os.environ["WINDIR"]
		cmd = "{windir}\\explorer.exe \"{path}\"".format(windir=windir, path=path)
		wx.CallAfter(subprocess.call, cmd, shell=True)
		self.Close()

	def onCloseButton(self, evt):
		_UserConfigurationsManager.setUserConfigurations(self.userConfigs)
		_UserConfigurationsManager.save()
		self.Destroy()

	@classmethod
	def run(cls):
		if isOpened(cls):
			return
		gui.mainFrame.prePopup()
		d = cls(gui.mainFrame)
		d.Show()
		gui.mainFrame.postPopup()


class UpdateFolderDialog(
	contextHelpEx.ContextHelpMixinEx,
	wx.Dialog):
	# Translators: this is the title of Update folder dialog.
	title = _("Preparation of %s folder")
	helpObj = getHelpObj("hdr30-1-3")

	def __init__(self, parent, folderPath):
		dialogTitle = self.title % os.path.basename(folderPath)
		dialogTitle = makeAddonWindowTitle(dialogTitle)
		self.preparedFolderPath = folderPath
		self.userConfigs = _UserConfigurationsManager .getUserConfigurations()
		super(UpdateFolderDialog, self).__init__(
			parent,
			wx.ID_ANY,
			title=dialogTitle,
			style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX
		)
		self.doGui()
		self.CentreOnScreen()

	def doGui(self):
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# Translators: This is the label of list box appearing
		# in the update or Prepare folder dialog.
		labelText = _("Import from &folder:")
		self.fromFoldersListBox = sHelper.addLabeledControl(
			labelText,
			wx.ListBox,
			choices=[],
		)
		# the buttons
		bHelper = gui.guiHelper.ButtonHelper(wx.HORIZONTAL)
		# translators: a label for a button in the update or Prepare folder dialog.
		labelText = _("Import &add-ons")
		self.importAddonsButton = bHelper.addButton(self, label=labelText)
		self.importAddonsButton.Bind(wx.EVT_BUTTON, self.onImportAddonsButton)
		# translators: a label for a button in the update or Prepare folder dialog.
		labelText = _("Import speech &dictionaries")
		self.importSpeechDictionariesButton = bHelper.addButton(self, label=labelText)
		self.importSpeechDictionariesButton.Bind(wx.EVT_BUTTON, self.onImportSpeechDictionariesButton)
		# translators: a label for a button in the update or Prepare folder dialog.
		labelText = _("Import ponctuation/symbol &pronunciations")
		self.importSymbolPrononciationsButton = bHelper.addButton(self, label=labelText)
		self.importSymbolPrononciationsButton.Bind(wx.EVT_BUTTON, self.onImportSymbolPrononciationsButton)
		# translators: a label for a button in the update or Prepare folder dialog.
		labelText = _("Import input &gesture changes")
		self.importGesturesButton = bHelper.addButton(self, label=labelText)
		self.importGesturesButton.Bind(wx.EVT_BUTTON, self.onImportGesturesButton)
		# translators: a label for a button in the update or Prepare folder dialog.
		labelText = _("Import configuration p&rofiles")
		self.importProfilesButton = bHelper.addButton(self, label=labelText)
		self.importProfilesButton.Bind(wx.EVT_BUTTON, self.onImportProfilesButton)
		# translators: a label for a button in the update or Prepare folder dialog.
		labelText = _("Import &NVDA parameters (normal configuration)")
		self.importNormalConfigurationButton = bHelper.addButton(self, label=labelText)
		self.importNormalConfigurationButton.Bind(wx.EVT_BUTTON, self.onImportNormalConfigurationButton)
		labelText = _("Import all the &configuration")
		importConfigurationButton = bHelper.addButton(self, label=labelText)
		importConfigurationButton.Bind(wx.EVT_BUTTON, self.onImportConfigurationButton)
		sHelper.addItem(bHelper)
		bHelper = sHelper.addDialogDismissButtons(
			gui.guiHelper.ButtonHelper(wx.HORIZONTAL))
		closeButton = bHelper.addButton(
			self, id=wx.ID_CLOSE, label=NVDAString("&Close"))
		closeButton.Bind(wx.EVT_BUTTON, lambda evt: self.Destroy())
		self.SetEscapeId(wx.ID_CLOSE)
		mainSizer.Add(
			sHelper.sizer, border=gui.guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		self.updateConfigurations()
		if self.fromFoldersListBox.Count:
			self.fromFoldersListBox.SetSelection(0)
		self.fromFoldersListBox.SetFocus()

	def isNVDAUserConfigurationFolder(self, path):
		if os.path.isdir(path):
			dirs = os.listdir(path)
			if "profiles" in dirs\
				and "updates" in dirs\
				and "nvda.ini" in dirs:
				return True
		return False

	def reportEndOfImport(self):
		def callback():
			api.processPendingEvents()
			time.sleep(0.1)
			speech.cancelSpeech()
			# Translators: message to user to report end of import.
			msg = _("Import terminated")
			queueHandler.queueFunction(
				queueHandler.eventQueue,
				ui.message,
				msg,
			)
			obj = api.getFocusObject()
			eventHandler.queueEvent("gainFocus", obj)
		wx.CallLater(100, callback)

	def updateConfigurations(self):
		self.configurations = []
		for dir in self.userConfigs:
			for folderName in self.userConfigs[dir]:
				path = os.path.join(dir, folderName)
				if path == self.preparedFolderPath:
					continue
				self.configurations.append(path)
		tempList = []
		for path in self.configurations:
			pre = ""
			if not self.isNVDAUserConfigurationFolder(path):
				pre += "?"
			if path == _UserConfigurationsManager.activeUserConfigPath:
				# checked symbol
				pre = chr(0x2713) + pre
			folderName = os.path.basename(path)
			dir = os.path.dirname(path)
			label = "%s %s (%s)" % (pre, folderName, dir)
			tempList.append(label)
		self.fromFoldersListBox .Clear()
		self.fromFoldersListBox .AppendItems(tempList)

	def getAddonsFromPath(self, path):
		addonDirNames = os.listdir(path)
		addonPaths = [os.path.join(path, name) for name in addonDirNames]
		from addonHandler import Addon
		from locale import strxfrm
		addons = []
		for path in addonPaths:
			if not os.path.isdir(path):
				continue
			addon = Addon(path)
			addons.append(addon)
		return sorted(addons, key=lambda a: strxfrm(a.manifest['summary']))

	def onImportAddonsButton(self, evt):
		index = self.fromFoldersListBox .GetSelection()
		path = self.configurations[index]
		fromAddonsPath = os.path.join(path, "addons")
		if not os.path.isdir(fromAddonsPath):
			# Translators: message to user there is no addon to import.
			ui.message(_("No addon to import"))
			return
		addons = self.getAddonsFromPath(fromAddonsPath)
		if len(addons) == 0:
			# Translators: message to user there is no addon to import.
			ui.message(_("No addon to import"))
			return
		with AddonImportDialog(self, self.preparedFolderPath, addons) as dlg:
			done = dlg.ShowModal()
			if done:
				addonPathsList = dlg.addonPathsList
			dlg.Destroy()

		def callback(addonPathsList):

			from ..utils import runInThread
			th = runInThread.RepeatBeep(
				delay=2.0, beep=(200, 200))
			th.start()
			for path in addonPathsList:
				name = os.path.basename(path)
				to = os.path.join(self.preparedFolderPath, "addons", name)
				if os.path.exists(to):
					th.stop()
					th = runInThread.RepeatBeep(
						delay=2.0, beep=(200, 200))
					if gui.messageBox(
						# Translators: message to report that add-on already exists and ask user to replace it.
						_("%s add-on exists. Do you want to replace it?") % name,
						# Translators: message box dialog title.
						_("Warning"),
						wx.YES | wx.NO | wx.ICON_WARNING) != wx.YES:
						th.start()
						continue
					th.start()
					shutil.rmtree(to)
				shutil.copytree(path, to)
			th.stop()
			del th
			self.reportEndOfImport()
		api.processPendingEvents()
		time.sleep(0.5)
		speech.cancelSpeech()
		if done:
			# Translators: message to user to wait.
			wx.CallLater(40, ui.message, _("Please wait"))
			wx.CallLater(1000, callback, addonPathsList)
			return
		obj = api.getFocusObject()
		eventHandler.queueEvent("gainFocus", obj)

	def onImportProfilesButton(self, evt):
		index = self.fromFoldersListBox .GetSelection()
		path = self.configurations[index]
		profilesPath = os.path.join(path, "profiles")
		if not os.path.isdir(profilesPath):
			# Translators: message to user there is no addon to import.
			ui.message(_("No profile to import"))
			return
		profilesList = os.listdir(profilesPath)
		if len(profilesList) == 0:
			# Translators: message to user there is no profile to import.
			ui.message(_("No profile to import"))
			return
		profilePaths = [os.path.join(profilesPath, profile) for profile in profilesList]
		with ProfilesImportDialog(self, self.preparedFolderPath, profilePaths) as dlg:
			done = dlg.ShowModal()
			dlg.Destroy()
		if done:
			self.reportEndOfImport()

	def onImportSpeechDictionariesButton(self, evt):
		index = self.fromFoldersListBox .GetSelection()
		fromPath = self.configurations[index]
		toPath = self.preparedFolderPath
		fromSpeechDictsPath = os.path.join(fromPath, "speechDicts")
		if not os.path.exists(fromSpeechDictsPath):
			# Translators: message to user that there is no speech dictionary to import.
			ui.message(_("No speech dictionary to import"))
			return
		speechDictionariesList = os.listdir(fromSpeechDictsPath)
		if len(speechDictionariesList) == 0:
			# Translators: message to user that there is no speech dictionary to import.
			ui.message(_("No speech dictionary to import"))
			return
		toSpeechDictsPath = os.path.join(toPath, "speechDicts")
		if os.path.exists(toSpeechDictsPath):
			if gui.messageBox(
				# Translators: message when speechDicts folder exists and will be replaced.
				_("The configuration folder contains already speech dictionaries. Do you want to replace them?"),
				# Translators: messageBox dialog.
				_("Warning"),
				wx.YES | wx.NO | wx.CANCEL | wx.NO_DEFAULT) != wx.YES:
				return
			shutil.rmtree(toSpeechDictsPath)
		# Translators: message to user to wait.
		ui.message(_("Please wait"))

		from ..utils import runInThread
		th = runInThread.RepeatBeep(
			delay=2.0, beep=(200, 200))
		th.start()
		shutil.copytree(fromSpeechDictsPath, toSpeechDictsPath)
		log.warning("onImportSpeechDictionariesButton: %s copied to %s" % (fromSpeechDictsPath, toSpeechDictsPath))
		th.stop()
		del th
		self.reportEndOfImport()

	def onImportSymbolPrononciationsButton(self, evt):
		index = self.fromFoldersListBox .GetSelection()
		fromPath = self.configurations[index]
		toPath = self.preparedFolderPath
		dirs = os.listdir(fromPath)
		fileNames = []
		for item in dirs:
			path = os.path.join(fromPath, item)
			if not os.path.isfile(path):
				continue
			if "symbols-" not in item and os.path.splitext(path)[1] != "dic":
				continue
			fileNames.append(item)
		if len(fileNames) == 0:
			# Translators: message to user to report no ponctuation\symbol prononunciations to import.
			ui.message(_("No ponctuation or symbol pronunciations to import"))
			return
		# check if there are already symbol
		dirs = os.listdir(toPath)
		exist = False
		for item in dirs:
			path = os.path.join(fromPath, item)
			if not os.path.isfile(path):
				continue
			if "symbols-" not in item and os.path.splitext(path)[1] != "dic":
				continue
			exist = True
			break
		replace = True
		if exist:
			ret = gui.messageBox(
				# Translators: message to report that there are already symbols pronunciations in configuration.
				_(
					"The configuration folder already contains symbol/punctuation pronunciations. "
					"Do you want to replace it?"),
				# Translators: message box dialog title.
				_("Warning"),
				wx.YES | wx.NO | wx.CANCEL | wx.NO_DEFAULT)
			if ret == wx.CANCEL:
				self.importSymbolPrononciationsButton.SetFocus()
				return
			elif ret == wx.NO:
				replace = False

		for name in fileNames:
			toSymbolPrononciationPath = os.path.join(toPath, name)
			if os.path.exists(toSymbolPrononciationPath) and not replace:
				continue
			fromSymbolPrononciationPath = os.path.join(fromPath, name)
			shutil.copy(fromSymbolPrononciationPath, toPath)
			log.warning("ImportSymbolPrononciationsButton: %s copied to %s" % (fromSymbolPrononciationPath, toPath))
		self.reportEndOfImport()

	def onImportGesturesButton(self, evt):
		index = self.fromFoldersListBox .GetSelection()
		fromPath = self.configurations[index]
		toPath = self.preparedFolderPath
		fromGesturesIniPath = os.path.join(fromPath, "gestures.ini")
		if not os.path.exists(fromGesturesIniPath):
			# Translators: message to user when there is no input gesture change to import.
			ui.message(_("No input gesture change to import"))
			return
		toGesturesIniPath = os.path.join(toPath, "gestures.ini")
		if os.path.exists(toGesturesIniPath):
			ret = gui.messageBox(
				# Translators: message to inform user that there are already input gesture changes.
				_("The configuration folder already contains input gesture changes. Do you want to replace them?"),
				# Translators: message box title.
				_("Warning"),
				wx.YES | wx.NO | wx.CANCEL | wx.NO_DEFAULT)
			if ret != wx.YES:
				self.importGesturesButton.SetFocus()
				return
		shutil.copy(fromGesturesIniPath, toPath)
		log.warning("onImportGesturesButton: %s copied to %s" % (fromGesturesIniPath, toPath))
		self.reportEndOfImport()

	def onImportNormalConfigurationButton(self, evt):
		index = self.fromFoldersListBox .GetSelection()
		fromPath = self.configurations[index]
		toPath = self.preparedFolderPath
		fromNVDAIniPath = os.path.join(fromPath, "nvda.ini")
		if not os.path.exists(fromNVDAIniPath):
			# Translators: message to user when there is no nvda normal configuration to import.
			ui.message(_("No NVDA normal configuration to import"))
			return
		toNVDAIniPath = os.path.join(toPath, "nvda.ini")
		if os.path.exists(toNVDAIniPath):
			ret = gui.messageBox(
				# Translators: message to inform user that there is already NVDA normal configuration .
				_("The configuration folder already contains NVDA normal configuration. Do you want to replace it?"),
				# Translators: message box title.
				_("Warning"),
				wx.YES | wx.NO | wx.CANCEL | wx.NO_DEFAULT)
			if ret != wx.YES:
				self.importNormalConfigurationButton.SetFocus()
				return
		shutil.copy(fromNVDAIniPath, toPath)
		log.warning("onImportNormalConfigurationButton: %s copied to %s" % (fromNVDAIniPath, toPath))
		self.reportEndOfImport()

	def onImportConfigurationButton(self, evt):
		if os.path.exists(self.preparedFolderPath):
			if os.listdir(self.preparedFolderPath):
				if gui.messageBox(
					# Translators: message to warn datas deletion.
					_(
						"""The "%s" folder contains data that will be erased during copying. """
						"""Do you still wish to continue?""") % (
						os.path.basename(self.preparedFolderPath)),
					# Translators: message box dialog title.
					_("Warning"),
					wx.YES | wx.NO | wx.ICON_WARNING) != wx.YES:
					return
		time.sleep(0.5)
		api.processPendingEvents()
		time.sleep(0.5)
		speech.cancelSpeech()
		index = self.fromFoldersListBox .GetSelection()
		fromFolderPath = self.configurations[index]

		def callback(fromFolderPath):
			from ..utils import runInThread
			th = runInThread.RepeatBeep(
				delay=2.0, beep=(200, 200))
			th.start()
			if os.path.exists(self.preparedFolderPath):
				shutil.rmtree(self.preparedFolderPath)

			shutil.copytree(fromFolderPath, self.preparedFolderPath)
			th.stop()
			del th
			self.reportEndOfImport()
			self.Close()
		# Translators: message to user to wait.
		speech.speakMessage(_("Please wait"))
		wx.CallLater(100, callback, fromFolderPath)


class PrepareFolderDialog(UpdateFolderDialog):
	# Translators: This is the title of the Prepare folder dialog.
	title = _("Preparation of %s folder")


class ModifyFolderDialog(UpdateFolderDialog):
	# Translators: This is the title of the modify user configuration dialog.
	title = _("Modification of %s folder")


class AddonImportDialog(
	contextHelpEx.ContextHelpMixinEx,
	wx.Dialog):
	title = None

	def __init__(self, parent, toFolderPath, addons):
		# Translators: This is the title of the Addons Import dialog.
		dialogTitle = _("Addons's import")
		AddonImportDialog.title = makeAddonWindowTitle(dialogTitle)
		self.addons = addons
		self.addonSummaries = [x.manifest["summary"] for x in self.addons]
		self.addonPaths = [addon.path for addon in self.addons]
		self.toFolderPath = toFolderPath
		super(AddonImportDialog, self).__init__(
			parent,
			wx.ID_ANY,
			self.title,
			style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX
		)
		self.doGui()
		self.CentreOnScreen()

	def doGui(self):
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# Translators: This is the label of list box appearing
		# on the Addon import dialog.
		labelText = _("&Add-ons:")
		self.addonsCheckListBox = sHelper.addLabeledControl(
			labelText,
			nvdaControls.CustomCheckListBox,
			choices=self.addonSummaries
		)
		# by default, check all add-ons
		self.addonsCheckListBox .SetCheckedStrings(self.addonSummaries)
		# the buttons
		bHelper = gui.guiHelper.ButtonHelper(wx.HORIZONTAL)
		# translators: this is a label for a button in addons import dialog.
		labelText = _("Check &all")
		checkAllButton = bHelper.addButton(self, label=labelText)
		checkAllButton .Bind(wx.EVT_BUTTON, self.onCheckAllButton)
		# translators: this is a label for a button in addons import dialog.
		labelText = _("&Uncheck all")
		unCheckAllButton = bHelper.addButton(self, label=labelText)
		unCheckAllButton .Bind(wx.EVT_BUTTON, self.onUnCheckAllButton)
		# translators: this is a label for a button in addons import dialog.
		labelText = _("&Delete existing add-ons")
		self.deleteExistingAddonsButton = bHelper.addButton(self, label=labelText)
		self.deleteExistingAddonsButton .Bind(wx.EVT_BUTTON, self.onDeleteExistingAddonsButton)
		# translators: this is a label for a button in addons import dialog.
		labelText = _("&Import")
		importButton = bHelper.addButton(self, label=labelText)
		importButton .Bind(wx.EVT_BUTTON, self.onImportButton)
		sHelper.addItem(bHelper)
		bHelper = sHelper.addDialogDismissButtons(
			gui.guiHelper.ButtonHelper(wx.HORIZONTAL))
		closeButton = bHelper.addButton(
			self, id=wx.ID_CLOSE, label=NVDAString("&Close"))
		closeButton.Bind(wx.EVT_BUTTON, lambda evt: self.Destroy())
		self.SetEscapeId(wx.ID_CLOSE)
		mainSizer.Add(
			sHelper.sizer, border=gui.guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		self.addonsCheckListBox .SetSelection(0)
		self.addonsCheckListBox .SetFocus()
		self.updateDeleteExistingAddonsButton()

	def onCheckAllButton(self, evt):
		self.addonsCheckListBox .SetCheckedStrings(self.addonSummaries)
		queueHandler.queueFunction(
			queueHandler.eventQueue,
			ui.message,
			# Translators: message to user to report that all items are checked.
			_("all items are checked")
		)
		obj = self.FindFocus()
		if obj == self.addonsCheckListBox:
			obj = api.getFocusObject()
			eventHandler.queueEvent("gainFocus", obj)
			return
		queueHandler.queueFunction(
			queueHandler.eventQueue,
			self.addonsCheckListBox .SetFocus)

	def onUnCheckAllButton(self, evt):
		self.addonsCheckListBox .SetCheckedStrings([])
		queueHandler.queueFunction(
			queueHandler.eventQueue,
			ui.message,
			# Translators: message to user to report that all items are unchecked.
			_("all items are unchecked")
		)
		obj = self.FindFocus()
		if obj == self.addonsCheckListBox:
			obj = api.getFocusObject()
			eventHandler.queueEvent("gainFocus", obj)
			return
		queueHandler.queueFunction(
			queueHandler.eventQueue,
			self.addonsCheckListBox .SetFocus)

	def updateDeleteExistingAddonsButton(self):
		toPath = os.path.join(self.toFolderPath, "addons")
		if not os.path.exists(toPath):
			self.deleteExistingAddonsButton.Disable()
		else:
			self.deleteExistingAddonsButton.Enable()

	def onDeleteExistingAddonsButton(self, evt):
		toAddonsFolderPath = os.path.join(self.toFolderPath, "addons")
		addons = os.listdir(toAddonsFolderPath)
		if len(addons):
			if gui.messageBox(
				# Translators: message to ask user if he want continue to delete current add-ons.
				_("Do you really want to delete all add-ons of %s folder?") % toAddonsFolderPath,
				# Translators: message box title
				_("confirmation"),
				wx.YES | wx.NO | wx.CANCEL) != wx.YES:
				return
		api.processPendingEvents()
		time.sleep(0.5)
		speech.cancelSpeech()

		def callback(toAddonsFolderPath):
			# Translators: message to user to wait.
			speech.speakMessage(_("Please wait"))
			from ..utils import runInThread
			th = runInThread.RepeatBeep(
				delay=2.0, beep=(200, 200))
			th.start()
			shutil.rmtree(toAddonsFolderPath)
			th.stop()
			del th
			self.updateDeleteExistingAddonsButton()
			# Translators: message to user to report end of deletion.
			ui.message(_("End of deletion"))
			obj = api.getFocusObject()
			eventHandler.queueEvent("gainFocus", obj)
		wx.CallLater(100, callback, toAddonsFolderPath)

	def onImportButton(self, evt):
		checkedAddons = self.addonsCheckListBox .GetChecked()
		if len(checkedAddons) == 0:
			# Translators: message to user to say that there is no addon checked.
			ui.message(_("there is no add-on checked"))
			return
		self.addonPathsList = []
		for index in checkedAddons:
			addonPath = self.addonPaths[index]
			self.addonPathsList.append(addonPath)
		self.EndModal(True)
		self.Close()


class NewUserConfigurationAddingDialog(
	contextHelpEx.ContextHelpMixinEx,
	wx.Dialog):
	# Translators: This is the title of the adding new folder dialog.
	title = _("Adding new folder")

	def __init__(self, parent):
		super(NewUserConfigurationAddingDialog, self).__init__(
			parent,
			wx.ID_ANY,
			title=self.title,
			style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX
		)
		self.parent = parent
		self.doGui()
		self.CentreOnScreen()

	def doGui(self):
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# Translators: This is the label of the edit field appearing
		# on the adding new folder  dialog.
		labelText = _("folder's userName:")
		self.configurationUserNameEdit = sHelper.addLabeledControl(
			labelText, wx.TextCtrl)
		self.configurationUserNameEdit .AppendText("")
		# Translators: This is the label of the edit field appearing
		# on the adding new folder dialog.
		labelText = _("folder's &location:")
		self.folderPathEdit = sHelper.addLabeledControl(
			labelText, wx.TextCtrl)
		self.folderPathEdit.AppendText(_UserConfigurationsManager .getLastSelectedUserConfigLocation())
		# the buttons
		bHelper = gui.guiHelper.ButtonHelper(wx.HORIZONTAL)
		# translators: this is a label for a button in adding new folder  dialog.
		labelText = _("&Browse...")
		browseButton = bHelper.addButton(self, label=labelText)
		browseButton.Bind(wx.EVT_BUTTON, self.onBrowseButton)
		sHelper.addItem(bHelper)
		bHelper = sHelper.addDialogDismissButtons(
			gui.guiHelper.ButtonHelper(wx.HORIZONTAL))
		# translators: this is a label for a button in adding new folder  dialog.
		labelText = _("&Add")
		addButton = bHelper.addButton(self, label=labelText)
		addButton.SetDefault()
		addButton.Bind(wx.EVT_BUTTON, self.onAddButton)
		cancelButton = bHelper.addButton(
			self,
			id=wx.ID_CLOSE,
			label=NVDAString("Cancel"))
		cancelButton.Bind(wx.EVT_BUTTON, lambda evt: self.Destroy())
		self.SetEscapeId(wx.ID_CLOSE)
		mainSizer.Add(
			sHelper.sizer, border=gui.guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		self.configurationUserNameEdit .SetFocus()

	def onBrowseButton(self, evt):
		# Translators: title of folder's selection dialog.
		dlg = wx.DirDialog(
			self,
			message=_("Folder's selection"),
			defaultPath=_UserConfigurationsManager .getLastSelectedUserConfigLocation())
		if dlg.ShowModal() == wx.ID_OK:
			dirName = dlg.GetPath()
			self.folderPathEdit.Clear()
			self.folderPathEdit.AppendText(dirName)
		dlg.Destroy()

	def isNVDAUserConfigurationFolder(self, path):
		if os.path.isdir(path):
			dirs = os.listdir(path)
			if "profiles" in dirs\
				and "updates" in dirs\
				and "nvda.ini" in dirs:
				return True
		return False

	def onAddButton(self, evt):
		# check configuration name and folder path
		if self.configurationUserNameEdit.GetValue() == "":
			queueHandler.queueFunction(
				queueHandler.eventQueue,
				ui.message,
				# Translators: message to user to ask for the username of configuration.
				_("you must specify the username of the folder")
			)
			self.configurationUserNameEdit.SetFocus()
			return
		elif self.folderPathEdit.GetValue() == "":
			queueHandler.queueFunction(
				queueHandler.eventQueue,
				ui.message,
				# Translators: message to user to ask for location of the configuration.
				_("You must specify the path to the location of the configuration")
			)
			self.folderPathEdit.SetFocus()
			return
		configurationUserName = self.configurationUserNameEdit.GetValue()
		folderName = _UserConfigurationsManager.getUserConfigFolderName(configurationUserName)
		folderPath = self.folderPathEdit.GetValue()
		self.newUserConfigFolderPath = os.path.join(folderPath, folderName)
		if self.newUserConfigFolderPath in self.parent.configurations:
			queueHandler.queueFunction(
				queueHandler.eventQueue,
				ui.message,
				# Translators: message to user to report folder already in the list.
				_("""The folder with "%s" username is already in the list of configuration folders """) % (
					os.path.basename(self.newUserConfigFolderPath))
			)
			queueHandler.queueFunction(
				queueHandler.eventQueue,
				ui.message,
				# Translators: message to user to ask an other username.
				_("choose another username")
			)
			obj = api.getFocusObject()
			eventHandler.queueEvent("gainFocus", obj)
			return
		if os.path.exists(self.newUserConfigFolderPath):
			if self.isNVDAUserConfigurationFolder(self.newUserConfigFolderPath):
				# Translators: message to report that the folder already exists and it's a nvda configuration
				# and ask to confirm adding.
				msg = _(
					"""The "%s" folder already exists and it's a nvda configuration folder. """
					"""Do you want to add it anyway?""")
			else:
				# Translators: message to report that the folder already exists and it's not  a nvda configuration
				# and ask to confirm adding.
				msg = _(
					"""The "%s" folder already exists and it's not a nvda configuration folder. """
					"""Do you want to add it anyway?""")
			if gui.messageBox(
				msg % os.path.basename(self.newUserConfigFolderPath),
				# Translators: message box dialog title.
				_("Warning"),
				wx.YES | wx.NO | wx.ICON_WARNING) != wx.YES:
				return
		_UserConfigurationsManager .setLastSelectedUserConfigLocation(folderPath)
		self.EndModal(True)
		self.Close()


class ExistingUserConfigurationAddingDialog(
	contextHelpEx.ContextHelpMixinEx,
	wx.Dialog):
	# Translators: This is the title of the Existing User Configuration Adding Dialog
	title = _("Adding existing folder")

	def __init__(self, parent):
		self.parent = parent
		super(ExistingUserConfigurationAddingDialog, self).__init__(
			parent,
			wx.ID_ANY,
			title=self.title,
			style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX
		)
		self.doGui()
		self.CentreOnScreen()

	def doGui(self):
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# Translators: This is the label of the edit field appearing
		# in the Existing User Configuration Adding Dialog.
		labelText = _("folder's &path:")
		self.folderPathEdit = sHelper.addLabeledControl(
			labelText, wx.TextCtrl)
		# the buttons
		bHelper = gui.guiHelper.ButtonHelper(wx.HORIZONTAL)
		# translators: this is a label for a button
		# in the Existing User Configuration Adding Dialog.
		labelText = _("&Browse...")
		browseButton = bHelper.addButton(self, label=labelText)
		browseButton.Bind(wx.EVT_BUTTON, self.onBrowseButton)
		sHelper.addItem(bHelper)
		bHelper = sHelper.addDialogDismissButtons(
			gui.guiHelper.ButtonHelper(wx.HORIZONTAL))
		# translators: this is a label for a button
		# in the Existing User Configuration Adding Dialog.
		labelText = _("&Add")
		addButton = bHelper.addButton(self, label=labelText)
		addButton.SetDefault()
		addButton.Bind(wx.EVT_BUTTON, self.onAddButton)
		cancelButton = bHelper.addButton(
			self,
			id=wx.ID_CLOSE,
			label=NVDAString("Cancel"))
		cancelButton.Bind(wx.EVT_BUTTON, lambda evt: self.Destroy())
		self.SetEscapeId(wx.ID_CLOSE)
		mainSizer.Add(
			sHelper.sizer, border=gui.guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		self.folderPathEdit .SetFocus()

	def onBrowseButton(self, evt):
		# Translators: title of folder's selection dialog.
		dlg = wx.DirDialog(
			self,
			message=_("Folder's selection"),
			defaultPath=_UserConfigurationsManager .getLastSelectedUserConfigLocation())
		if dlg.ShowModal() == wx.ID_OK:
			dirName = dlg.GetPath()
			self.folderPathEdit.Clear()
			self.folderPathEdit.AppendText(dirName)
		dlg.Destroy()

	def onAddButton(self, evt):
		# check configuration name and folder path
		if self.folderPathEdit.GetValue() == "":
			queueHandler.queueFunction(
				queueHandler.eventQueue,
				ui.message,
				# Translators: message to user to ask for location of the configuration.
				_("You must specify the path to the location of the configuration")
			)
			self.folderPathEdit.SetFocus()
			return
		self.newUserConfigFolderPath = self.folderPathEdit.GetValue()
		if self.newUserConfigFolderPath in self.parent.configurations:
			queueHandler.queueFunction(
				queueHandler.eventQueue,
				ui.message,
				# Translators: message to user to report folder already in the list.
				_(
					"""The folder with "%s" username is already in the list of configuration folders """) % (
						os.path.basename(self.newUserConfigFolderPath))
			)
		# check if it's a nvda user configuration
		dirs = os.listdir(self.newUserConfigFolderPath)
		if not (
			"addons" in dirs
			and "profiles" in dirs
			and "speechDicts" in dirs):
			queueHandler.queueFunction(
				queueHandler.eventQueue,
				ui.message,
				# Translators: message to user to indicate that the folder is not an user configuration folder.
				_("The folder is not user configuration's folder")
			)
			return
		self.EndModal(True)
		self.Close()


class ProfilesImportDialog(
	contextHelpEx.ContextHelpMixinEx,
	wx.Dialog):
	title = None

	def __init__(self, parent, toFolderPath, profilePaths):
		# Translators: This is the title of the Profiles import dialog.
		dialogTitle = _("Configuration profiles's import")
		ProfilesImportDialog.title = makeAddonWindowTitle(dialogTitle)
		from locale import strxfrm
		self.profilePaths = sorted(profilePaths)
		self.profilePaths = sorted(profilePaths, key=lambda a: strxfrm(a))
		self.toFolderPath = toFolderPath
		self.profiles = [os.path.basename(x).split(".")[0] for x in self.profilePaths]
		super(ProfilesImportDialog, self).__init__(
			parent,
			wx.ID_ANY,
			self.title,
			style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX,
		)
		self.doGui()
		self.CentreOnScreen()

	def doGui(self):
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# Translators: This is the label of list box appearing
		# on the Profiles Import dialog.
		labelText = _("&Profiles:")
		self.profilesCheckListBox = sHelper.addLabeledControl(
			labelText,
			nvdaControls.CustomCheckListBox,
			choices=self.profiles
		)
		self.profilesCheckListBox .SetCheckedStrings(self.profiles)
		# the buttons
		bHelper = gui.guiHelper.ButtonHelper(wx.HORIZONTAL)
		# translators: this is a label for a button in Profiles Import Dialog.
		labelText = _("Check &all")
		checkAllButton = bHelper.addButton(self, label=labelText)
		checkAllButton .Bind(wx.EVT_BUTTON, self.onCheckAllButton)
		# translators: this is a label for a button in Profiles Import Dialog.
		labelText = _("&Uncheck all")
		unCheckAllButton = bHelper.addButton(self, label=labelText)
		unCheckAllButton .Bind(wx.EVT_BUTTON, self.onUnCheckAllButton)
		# translators: this is a label for a button in Profiles Import Dialog.
		labelText = _("&Delete existing profiles")
		self.deleteExistingProfilesButton = bHelper.addButton(self, label=labelText)
		self.deleteExistingProfilesButton .Bind(wx.EVT_BUTTON, self.onDeleteExistingProfilesButton)
		# translators: this is a label for a button in Profiles Import Dialog.
		labelText = _("&Import")
		importButton = bHelper.addButton(self, label=labelText)
		importButton .Bind(wx.EVT_BUTTON, self.onImportButton)
		sHelper.addItem(bHelper)
		bHelper = sHelper.addDialogDismissButtons(
			gui.guiHelper.ButtonHelper(wx.HORIZONTAL))
		closeButton = bHelper.addButton(
			self, id=wx.ID_CLOSE, label=NVDAString("&Close"))
		closeButton.Bind(wx.EVT_BUTTON, lambda evt: self.Destroy())
		self.SetEscapeId(wx.ID_CLOSE)
		mainSizer.Add(
			sHelper.sizer, border=gui.guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		self.profilesCheckListBox .SetSelection(0)
		self.profilesCheckListBox .SetFocus()
		self.updateDeleteExistingProfilesButton()

	def onCheckAllButton(self, evt):
		self.profilesCheckListBox .SetCheckedStrings(self.profiles)
		queueHandler.queueFunction(
			queueHandler.eventQueue,
			ui.message,
			# Translators: message to user to report that all items are checked.
			_("all items are checked")
		)
		obj = self.FindFocus()
		if obj == self.profilesCheckListBox:
			obj = api.getFocusObject()
			eventHandler.queueEvent("gainFocus", obj)
			return
		queueHandler.queueFunction(
			queueHandler.eventQueue,
			self.profilesCheckListBox .SetFocus)

	def onUnCheckAllButton(self, evt):
		self.profilesCheckListBox .SetCheckedStrings([])
		queueHandler.queueFunction(
			queueHandler.eventQueue,
			ui.message,
			# Translators: message to user to report that all items are unchecked.
			_("all items are unchecked")
		)
		obj = self.FindFocus()
		if obj == self.profilesCheckListBox:
			obj = api.getFocusObject()
			eventHandler.queueEvent("gainFocus", obj)
			return
		queueHandler.queueFunction(
			queueHandler.eventQueue,
			self.profilesCheckListBox .SetFocus)

	def updateDeleteExistingProfilesButton(self):
		toPath = os.path.join(self.toFolderPath, "profiles")
		if not os.path.exists(toPath):
			self.deleteExistingProfilesButton.Disable()
		else:
			self.deleteExistingProfilesButton.Enable()

	def onDeleteExistingProfilesButton(self, evt):
		toProfilesFolderPath = os.path.join(self.toFolderPath, "profiles")
		profiles = os.listdir(toProfilesFolderPath)
		if len(profiles):
			if gui.messageBox(
				# Translators: message to ask user if he want continue to delete current profiles.
				_("Do you really want to delete all profiles of %s folder?") % toProfilesFolderPath,
				# Translators: message box title
				_("confirmation"),
				wx.YES | wx.NO | wx.CANCEL) != wx.YES:
				return
		api.processPendingEvents()
		time.sleep(0.5)
		speech.cancelSpeech()

		def callback(toProfilesFolderPath):
			# Translators: message to user to wait.
			speech.speakMessage(_("Please wait"))
			from ..utils import runInThread
			th = runInThread.RepeatBeep(
				delay=2.0, beep=(200, 200))
			th.start()
			shutil.rmtree(toProfilesFolderPath)
			th.stop()
			del th
			self.updateDeleteExistingProfilesButton()
			# Translators: message to user to report end of deletion.
			ui.message(_("End of deletion"))
			obj = api.getFocusObject()
			eventHandler.queueEvent("gainFocus", obj)
		wx.CallLater(100, callback, toProfilesFolderPath)

	def onImportButton(self, evt):
		checkedItems = self.profilesCheckListBox .GetCheckedItems()
		if len(checkedItems) == 0:
			# Translators: there is no profile checked.
			ui.message(_("There is no profile checked"))
			return
		profilePaths = [self.profilePaths[x] for x in checkedItems]
		# Translators: message to user to wait.
		speech.speakMessage(_("Please wait"))
		toProfilesPath = os.path.join(self.toFolderPath, "profiles")
		for path in profilePaths:
			name = os.path.basename(path)
			to = os.path.join(self.toFolderPath, "profiles", name)
			if os.path.exists(to):
				if gui.messageBox(
					# Translators: message to report that profile already exists and ask user to replace it.
					_("%s profile exists. Do you want to replace it?") % name.split(".")[0],
					# Translators: message box dialog title.
					_("Warning"),
					wx.YES | wx.NO | wx.ICON_WARNING) != wx.YES:
					continue
			if not os.path.exists(toProfilesPath):
				try:
					os.makedirs(toProfilesPath)
				except OSError:
					if not os.path.exists(toProfilesPath):
						log.error("Impossible to create the folder: %s" % toProfilesPath)
						# Translators: message to user to report error on creation of folder.
						ui.message(_("Impossible to import profils"))
						return
			shutil.copy(path, to)
		self.EndModal(True)
		self.Close()


_UserConfigurationsManager = UserConfigurationsManager()
