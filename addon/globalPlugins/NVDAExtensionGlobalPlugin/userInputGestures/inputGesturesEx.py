# globalPlugins\NVDAExtensionGlobalPlugin\userConfig\inputGestures.py
# a part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2021-2023 Paulber19
# This file is covered by the GNU General Public License.
# from a Javi Dominguez's idea  and some code  of it "commandHelper" add-on


import addonHandler
from logHandler import log
import api
import wx
import speech
import gui
import gui.guiHelper as guiHelper
import scriptHandler
from keyboardHandler import KeyboardInputGesture
import inputCore
from gui.inputGestures import InputGesturesDialog, _InputGesturesViewModel, _GesturesTree
from ..utils.NVDAStrings import NVDAString
from ..utils import getHelpObj, contextHelpEx


addonHandler.initTranslation()


def onInputGesturesCommandEx(evt):
	gui.mainFrame._popupSettingsDialog(InputGesturesDialogEx)


def initialize():
	gui.mainFrame.onInputGesturesCommand = onInputGesturesCommandEx
	log.debug(
		"gui.mainFrame.onInputGesturesCommand patched by: %s of %s module "
		% (onInputGesturesCommandEx.__name__, onInputGesturesCommandEx.__module__))

	menus = gui.mainFrame.sysTrayIcon.preferencesMenu.GetMenuItems()
	item = None
	for menuItem in menus:
		if menuItem.GetItemLabel() == NVDAString("I&nput gestures..."):
			item = menuItem
			break
	if item is not None:
		gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, onInputGesturesCommandEx, item)
		log.debug("%s of %s module is now the action for the  Input gestures  sub-menu " % (
			onInputGesturesCommandEx.__name__, onInputGesturesCommandEx.__module__))


class InputGesturesDialogEx(
	contextHelpEx.ContextHelpMixinEx,
	InputGesturesDialog):
	refreshButtonStateDelay = None
	_executeScriptWaitingTimer = None
	repeatCount = 0

	def __init__(self, parent: "InputGesturesDialog"):
		self.helpId = InputGesturesDialog.helpId
		self.focus = gui.mainFrame.prevFocus
		super(InputGesturesDialogEx, self).__init__(parent)

	def makeSettings(self, settingsSizer):
		filterSizer = wx.BoxSizer(wx.HORIZONTAL)
		# Translators: The label of a text field to search for gestures in the Input Gestures dialog.
		from ..utils.NVDAStrings import NVDAString_pgettext
		labelText = NVDAString_pgettext("inputGestures", "&Filter by:")
		filterLabel = wx.StaticText(self, label=labelText)
		self.filterCtrl = filterCtrl = wx.TextCtrl(self)
		filterSizer.Add(filterLabel, flag=wx.ALIGN_CENTER_VERTICAL)
		filterSizer.AddSpacer(guiHelper.SPACE_BETWEEN_ASSOCIATED_CONTROL_HORIZONTAL)
		filterSizer.Add(filterCtrl, proportion=1)
		settingsSizer.Add(filterSizer, flag=wx.EXPAND)
		settingsSizer.AddSpacer(5)
		filterCtrl.Bind(wx.EVT_TEXT, self.onFilterChange, filterCtrl)

		self.gesturesVM = _InputGesturesViewModel()
		tree = self.tree = _GesturesTree(self, self.gesturesVM)
		tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.onTreeSelect)
		settingsSizer.Add(tree, proportion=1, flag=wx.EXPAND)

		settingsSizer.AddSpacer(guiHelper.SPACE_BETWEEN_ASSOCIATED_CONTROL_VERTICAL)

		bHelper = guiHelper.ButtonHelper(wx.HORIZONTAL)
		# Translators: The label of a button to run the script in the Input Gestures dialog.
		self.executeScriptButton = bHelper.addButton(self, label=_("&Execute the script"))
		self.executeScriptButton.Bind(wx.EVT_BUTTON, self.onExecuteScriptButton)
		self.executeScriptButton.Disable()
		self.bindHelpEvent(getHelpObj("hdr205"), self.executeScriptButton)
		# Translators: The label of a button to add a gesture in the Input Gestures dialog.
		self.addButton = bHelper.addButton(self, label=NVDAString("&Add"))
		self.addButton.Bind(wx.EVT_BUTTON, self.onAdd)
		self.addButton.Disable()

		# Translators: The label of a button to remove a gesture in the Input Gestures dialog.
		self.removeButton = bHelper.addButton(self, label=NVDAString("&Remove"))
		self.removeButton.Bind(wx.EVT_BUTTON, self.onRemove)
		self.removeButton.Disable()

		bHelper.sizer.AddStretchSpacer()
		# Translators: The label of a button to reset all gestures in the Input Gestures dialog.
		resetButton = wx.Button(self, label=NVDAString("Reset to factory &defaults"))
		bHelper.sizer.Add(resetButton)
		resetButton.Bind(wx.EVT_BUTTON, self.onReset)

		settingsSizer.Add(bHelper.sizer, flag=wx.EXPAND)
		self.tree.Bind(wx.EVT_WINDOW_DESTROY, self._onDestroyTree)
		self.tree.Bind(wx.EVT_TREE_KEY_DOWN, self.onKeyDown)

	def postInit(self):
		super(InputGesturesDialogEx, self).postInit()
		try:
			mod = self.focus.appModule.__module__
		except Exception:
			return
		allGestures = self.tree.gesturesVM.allGestures
		catToSelect = None
		for cat in allGestures:
			for scr in cat.scripts:
				scriptMod = scr.scriptInfo.moduleName
				scriptMod = ".".join(scriptMod.split(".")[:2])
				if scriptMod.startswith(mod):
					catToSelect = cat.displayName
					break
		if not catToSelect:
			return
		count = self.tree.GetCount()
		rootItem = self.tree.GetRootItem()
		(item, cookie) = self.tree.GetFirstChild(rootItem)
		for i in range(0, count):
			if not item:
				break
			itemText = self.tree.GetItemText(item)
			if itemText == catToSelect:
				self.tree.SelectItem(item)
				self.tree.Expand(item)
				break
			(item, cookie) = self.tree.GetNextChild(item, cookie)

	def onKeyDown(self, evt):
		keyCode = evt.GetKeyCode()
		if keyCode == wx.WXK_SPACE and self.executeScriptButton.Enabled:
			self.onExecuteScriptButton(evt)
			return
		evt.Skip()

	def getScript(self, item):

		def smallBeep():
			if False:
				from tones import beep
				beep(300, 30)
			return

		if not item or not hasattr(item, "scriptInfo"):
			return
		ti = getattr(self.focus, "treeInterceptor", None)
		scriptInfo = item.scriptInfo
		log.debug("scriptinfo: %s, %s, %s" % (scriptInfo.className, scriptInfo.moduleName, scriptInfo.scriptName))
		module = scriptInfo.moduleName.split(".")
		if scriptInfo.scriptName.startswith("kb:"):
			script = scriptHandler._makeKbEmulateScript(scriptInfo.scriptName)
			if script:
				smallBeep()
				return script
		if ti:
			script = getattr(ti, "script_%s" % scriptInfo.scriptName, None)
			if script:
				smallBeep()
				return script

		if scriptInfo.className == "GlobalCommands":
			import globalCommands
			script = getattr(globalCommands.commands, "script_" + scriptInfo.scriptName)
			if script:
				smallBeep()
				return script

		if scriptInfo.className == "ConfigProfileActivationCommands":
			import globalCommands
			script = getattr(globalCommands.configProfileActivationCommands, "script_" + scriptInfo.scriptName)
			if script:
				smallBeep()
				return script
		if module[0] == "globalPlugins":
			import globalPluginHandler
			plugins = list(globalPluginHandler .runningPlugins)
			gp = ".".join(module[:2])
			for p in plugins:
				m = p.__module__
				if gp in m:
					i = plugins .index(p)
					script = getattr(list(plugins)[i], "script_%s" % scriptInfo.scriptName, None)
					if script:
						smallBeep()
						return script
		if scriptInfo.className == "AppModule":
			script = getattr(self.focus.appModule, "script_" + scriptInfo.scriptName, None)
			if script:
				smallBeep()
				return script
		if module[0] == "appModules":
			script = getattr(self.focus, "script_" + scriptInfo.scriptName, None)
			if script:
				smallBeep()
				return script

		script = getattr(self.focus, "script_" + scriptInfo.scriptName, None)
		if script:
			smallBeep()
			return script
		return None

	def onTreeSelect(self, evt):
		if evt:
			evt.Skip()
		if self.refreshButtonStateDelay is not None:
			self.refreshButtonStateDelay.Stop()
			# to work around the NVDA bug that generates a series of errors in the log,
			# when entering text in the "Filter by" field
			# the refreshItems on the tree generates an onTreeSelect for each item.
			# so wait for the last item to refresh buttons
		self.refreshButtonStateDelay = wx.CallLater(50, self._refreshButtonState)

	def _refreshButtonState(self):
		if self.refreshButtonStateDelay is not None:
			self.refreshButtonStateDelay.Stop()
			self.refreshButtonStateDelay = None
		selectedItems = self.tree.getSelectedItemData()
		if selectedItems is None:
			item = None
		else:
			# get the leaf of the selection
			item = next((item for item in reversed(selectedItems) if item is not None), None)
		pendingAdd = self.gesturesVM.isExpectingNewEmuGesture or self.gesturesVM.isExpectingNewGesture
		self.addButton.Enabled = bool(item and item.canAdd and not pendingAdd)
		log.debug("addButtonEnabled: %s" % self.addButton.Enabled)
		self.removeButton.Enabled = bool(item and item.canRemove and not pendingAdd)
		script = self.getScript(item) if self.addButton.Enabled else None
		log.debug("refreshButton: script = %s" % script)
		self.executeScriptButton.Enabled = bool(script and self.addButton.Enabled)
		if self.executeScriptButton.Enabled:
			self.executeScriptButton.SetDefault()

	def _executeScript(self, script, gestureOrgestureCls, count):
		api.processPendingEvents()
		speech.cancelSpeech()
		for i in range(0, count + 1):
			speech.cancelSpeech()
			scriptHandler.executeScript(script, gestureOrgestureCls)

	def onExecuteScriptButton(self, evt):

		def callback(script, gestureOrgestureCls):
			self._executeScriptWaitingTimer = None
			wx.CallLater(200, speech.cancelSpeech)
			wx.CallLater(500, self._executeScript, script, gestureOrgestureCls, self.repeatCount)
			self.Destroy()

		self.repeatCount = self.repeatCount + 1 if self._executeScriptWaitingTimer is not None else 0
		if self._executeScriptWaitingTimer is not None:
			self._executeScriptWaitingTimer.Stop()
			self._executeScriptWaitingTimer = None
		selectedItems = self.tree.getSelectedItemData()
		if selectedItems is None:
			item = None
		else:
			# get the leaf of the selection
			item = next((item for item in reversed(selectedItems) if item is not None), None)
		if not item:
			return
		scriptInfo = item.scriptInfo
		script = self.getScript(item)
		if not script:
			log.error("no script to run: %s, %s, %s" % (
				scriptInfo.scriptName, scriptInfo.className, scriptInfo.moduleName))
			return
		try:
			gestureCls = inputCore._getGestureClsForIdentifier(scriptInfo.gestures[0])
		except Exception:
			gestureCls = KeyboardInputGesture
		gesture = None
		if gestureCls == KeyboardInputGesture and len(scriptInfo.gestures):
			identifier = scriptInfo.gestures[0]
			key = identifier.split(":", 1)[1]
			gesture = KeyboardInputGesture.fromName(key)
		gestureOrGestureCls = gesture if gesture else gestureCls
		from ..settings import _addonConfigManager
		delay = _addonConfigManager.getMaximumDelayBetweenSameScript()
		self._executeScriptWaitingTimer = wx.CallLater(delay, callback, script, gestureOrGestureCls)
