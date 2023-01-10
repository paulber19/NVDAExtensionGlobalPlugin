# globalPlugins\NVDAExtensionGlobalPlugin\userInputGestures/__init__.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2016 - 2022 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import addonHandler
from logHandler import log
import os
import globalVars
import wx
import sys
import gui
import inputCore
from ..utils.NVDAStrings import NVDAString
from ..utils import makeAddonWindowTitle, getHelpObj
from ..utils import contextHelpEx
addonHandler.initTranslation()


class UserInputGesturesDialog(
	contextHelpEx.ContextHelpMixinEx,
	gui.SettingsDialog):
	# Translators: The title of the user Input Gestures dialog
	# where the user can remap user input gestures for commands.
	title = _("User input Gestures")
	# help in the user manual.
	helpObj = getHelpObj("hdr20")

	def __init__(self, parent):
		self.title = makeAddonWindowTitle(self.title)
		super(UserInputGesturesDialog, self).__init__(parent)

	def makeSettings(self, settingsSizer):
		tree = self.tree = wx.TreeCtrl(
			self,
			size=wx.Size(600, 400),
			style=wx.TR_HAS_BUTTONS | wx.TR_HIDE_ROOT | wx.TR_LINES_AT_ROOT | wx.TR_SINGLE)
		self.treeRoot = tree.AddRoot("root")
		tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.onTreeSelect)
		settingsSizer.Add(tree, proportion=1, flag=wx.EXPAND)
		self.populateTree()
		settingsSizer.AddSpacer(
			gui.guiHelper.SPACE_BETWEEN_ASSOCIATED_CONTROL_VERTICAL)
		bHelper = gui.guiHelper.ButtonHelper(wx.HORIZONTAL)
		# Translators: The label of a button to remove a gesture
		# in the user Input Gestures dialog.
		self.removeButton = bHelper.addButton(self, label=_("&Remove"))
		self.removeButton.Bind(wx.EVT_BUTTON, self.onRemove)
		self.removeButton.Disable()
		# Translators: The label of a button to remove all gesture
		# in the user Input Gestures dialog.
		self.removeAllButton = bHelper.addButton(self, label=_("Remove &all"))
		self.removeAllButton.Bind(wx.EVT_BUTTON, self.onRemoveAll)
		self.pendingRemoves = set()
		settingsSizer.Add(bHelper.sizer)
		self.tree.Bind(wx.EVT_WINDOW_DESTROY, self._onDestroyTree)

	def postInit(self):
		self.tree.SetFocus()

	def populateTree(self):
		GestureMappingsRetriever = _UserGestureMappingsRetriever(
			obj=gui.mainFrame.prevFocus,
			ancestors=gui.mainFrame.prevFocusAncestors)
		self.gestures = GestureMappingsRetriever.results
		self.userGestureMap = GestureMappingsRetriever.userGestureMap
		for category in sorted(self.gestures):
			treeCat = self.tree.AppendItem(self.treeRoot, category)
			commands = self.gestures[category]
			for command in sorted(commands):
				treeCom = self.tree.AppendItem(treeCat, command)
				commandInfo = commands[command]
				self.tree.SetItemData(treeCom, commandInfo)
				for gesture in commandInfo.gestures:
					treeGes = self.tree.AppendItem(treeCom, self._formatGesture(gesture))
					self.tree.SetItemData(treeGes, gesture)
			if not self.tree.ItemHasChildren(treeCat):
				self.tree.Delete(treeCat)

	def _formatGesture(self, identifier):
		try:
			source, main = inputCore.getDisplayTextForGestureIdentifier(identifier)
			# Translators: Describes a gesture in the Input Gestures dialog.
			# {main} is replaced with the main part of the gesture; e.g. alt+tab.
			# {source} is replaced with the gesture's source; e.g. laptop keyboard.
			return _("{main} ({source})").format(main=main, source=source)
		except LookupError:
			return identifier

	def onTreeSelect(self, evt):
		try:
			item = self.tree.Selection
		except RuntimeError:
			return
		data = self.tree.GetItemData(item)
		isGesture = isinstance(data, str)
		if isGesture:
			self.removeButton.Enable()
		else:
			self.removeButton.Disable()

	def onRemove(self, evt):
		treeGes = self.tree.Selection
		gesture = self.tree.GetItemData(treeGes)
		treeCom = self.tree.GetItemParent(treeGes)
		scriptInfo = self.tree.GetItemData(treeCom)
		entry = (
			gesture,
			scriptInfo.moduleName,
			scriptInfo.className,
			scriptInfo.scriptName)
		self.pendingRemoves.add(entry)
		self.tree.Delete(treeGes)
		scriptInfo.gestures.remove(gesture)
		self.tree.SetFocus()
		self.onTreeSelect(evt)

	def onRemoveAll(self, evt):
		if gui.messageBox(
			# Translators: the label of a message box dialog.
			_("Do you really want to erase all the modifications of input gesture that have been made?"),
			# Translators: the title of a message box dialog.
			_("Warning"),
			wx.YES | wx.NO | wx.ICON_WARNING) == wx.NO:
			return
		inputCore.manager.userGestureMap.clear()
		inputCore.manager.userGestureMap.save()

	def _onDestroyTree(self, evt: wx.WindowDestroyEvent):
		# Remove the binding when the tree is destroyed so that it can not be called during destruction
		# of the dialog.
		self.tree.Unbind(wx.EVT_TREE_SEL_CHANGED)

	def onOk(self, evt):
		for gesture, module, className, scriptName in self.pendingRemoves:
			try:
				self.userGestureMap.remove(gesture, module, className, scriptName)
			except ValueError:
				pass
		if self.pendingRemoves:
			# Only save if there is something to save.
			try:
				self.userGestureMap.save()
			except Exception:
				log.debugWarning("", exc_info=True)
				# Translators: An error displayed
				# when saving user defined input gestures fails.
				gui.messageBox(
					NVDAString("Error saving user defined gestures - probably read only file system."),
					NVDAString("Error"), wx.OK | wx.ICON_ERROR)
		inputCore.manager.loadUserGestureMap()
		super(UserInputGesturesDialog, self).onOk(evt)


class _UserGestureMappingsRetriever(inputCore._AllGestureMappingsRetriever):
	def __init__(self, obj, ancestors):
		self.results = {}
		self.scriptInfo = {}
		self.handledGestures = set()
		self.resultsWithNoScript = set()
		self.userGestureMap = UserGestureMap()
		self.userGestureMap.clear()
		try:
			self.userGestureMap.load(
				os.path.join(globalVars.appArgs.configPath, "gestures.ini"))
		except IOError:
			log.debugWarning("No user gesture map")
			return
		self.addGlobalMap(self.userGestureMap)

	def addToResults(self, scriptInfo):
		if scriptInfo.category not in self.results:
			self.results[scriptInfo.category] = {}
		self.results[scriptInfo.category][scriptInfo.displayName] = scriptInfo

	def addGlobalMap(self, gmap):
		for cls, moduleName, className, gesture, scriptName in gmap.getScriptsForAllGestures():
			c = "%s.%s" % (moduleName, className)
			key = (c, gesture)
			if key in self.handledGestures:
				continue
			self.handledGestures.add(key)
			try:
				scriptInfo = self.scriptInfo[cls, scriptName]
			except KeyError:
				try:
					script = getattr(cls, "script_%s" % scriptName)
				except AttributeError:
					script = None
				scriptInfo = self.makeNormalScriptInfo(
					cls, moduleName, className, scriptName, script)
				if not scriptInfo:
					continue
				self.scriptInfo[scriptInfo.cls, scriptInfo.scriptName] = scriptInfo
				self.addToResults(scriptInfo)
			scriptInfo.gestures.append(gesture)

	def makeNormalScriptInfo(
		self,
		cls,
		moduleName,
		className,
		scriptName,
		script):
		info = inputCore.AllGesturesScriptInfo(cls, scriptName)
		category = inputCore._AllGestureMappingsRetriever.getScriptCategory(cls, script)
		if category is None:
			category = "%s.%s" % (moduleName, className)
		info.category = category
		if script is None:
			if scriptName:
				if scriptName.startswith("kb:"):
					info.category = NVDAString("%s") % inputCore.SCRCAT_KBEMU
					info.displayName = NVDAString(
						"Emulate key press: {emulateGesture}").format(emulateGesture=scriptName[3:])
				else:
					info.displayName = scriptName
			else:
				info.displayName = _("Deleted gestures")
		else:
			info.displayName = script.__doc__
			if not info.displayName:
				return None
		return info


class UserGestureMap(inputCore.GlobalGestureMap):
	def getScriptsForGesture(self, gesture):
		try:
			scripts = self._map[gesture]
		except KeyError:
			return
		for moduleName, className, scriptName in scripts:
			try:
				module = sys.modules[moduleName]
				cls = getattr(module, className)
			except Exception:
				cls = None
			yield cls, moduleName, className, scriptName

	def getScriptsForAllGestures(self):
		"""Get all of the scripts and their gestures.
		@return: The Python class, gesture and script name for each mapping;
			the script name may be C{None}
			indicating that the gesture should be unbound for this class.
		@rtype: generator of (class, str, str)
		"""
		for gesture in self._map:
			for cls, moduleName, className, scriptName in self.getScriptsForGesture(gesture):
				yield cls, moduleName, className, gesture, scriptName
