	# -*- coding: UTF-8 -*-
	#NVDAExtensionGlobalPlugin/userInputGestures/__init__.py
#A part of NVDAExtensionGlobalPlugin add-on
#Copyright (C) 2016  paulber19
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.

#NVDAExtensionGlobalPlugin/userInputGestures/__init__.py
#settingsDialogs.py
#A part of NonVisual Desktop Access (NVDA)
#Copyright (C) 2017 paulber19
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.
import addonHandler
addonHandler.initTranslation()
import os
import globalVars
import wx
import gui
import sys
import api
from logHandler import log
import braille
from gui import guiHelper
from gui.settingsDialogs import SettingsDialog, InputGesturesDialog
import inputCore
import configobj
from fileUtils import FaultTolerantFile
import baseObject
from ..utils.NVDAStrings import NVDAString
from ..utils import makeAddonWindowTitle

# constant
C_ONLYADDED = 0
C_ONLYDELETED = 1


class UserInputGesturesDialog(gui.SettingsDialog):
	# Translators: The title of the user Input Gestures dialog where the user can remap user input gestures for commands.
	title = _("User  input Gestures")
	def __init__(self, parent):
		self.title = makeAddonWindowTitle(self.title)
		super(UserInputGesturesDialog, self).__init__(parent)
	
	def makeSettings(self, settingsSizer):
		tree = self.tree = wx.TreeCtrl(self, size=wx.Size(600, 400), style=wx.TR_HAS_BUTTONS | wx.TR_HIDE_ROOT | wx.TR_LINES_AT_ROOT | wx.TR_SINGLE )
		self.treeRoot = tree.AddRoot("root")
		tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.onTreeSelect)
		settingsSizer.Add(tree, proportion=1, flag=wx.EXPAND)
		GestureMappingsRetriever = _UserGestureMappingsRetriever(obj=gui.mainFrame.prevFocus, ancestors=gui.mainFrame.prevFocusAncestors)
		self.gestures = GestureMappingsRetriever.results
		self.userGestureMap = GestureMappingsRetriever.userGestureMap
		self.populateTree()
		settingsSizer.AddSpacer(guiHelper.SPACE_BETWEEN_ASSOCIATED_CONTROL_VERTICAL)
		bHelper = guiHelper.ButtonHelper(wx.HORIZONTAL)
		# Translators: The label of a button to remove a gesture in the user Input Gestures dialog.
		self.removeButton = bHelper.addButton(self, label=_("&Remove"))
		self.removeButton.Bind(wx.EVT_BUTTON, self.onRemove)
		self.removeButton.Disable()
		# Translators: The label of a button to remove all gesture in the user Input Gestures dialog.
		self.removeAllButton = bHelper.addButton(self, label=_("Remove &all"))
		self.removeAllButton.Bind(wx.EVT_BUTTON, self.onRemoveAll)
		self.pendingRemoves = set()
		settingsSizer.Add(bHelper.sizer)

	def postInit(self):
		self.tree.SetFocus()

	
	def populateTree(self, filter=''):
		for category in sorted(self.gestures):
			treeCat = self.tree.AppendItem(self.treeRoot, category)
			commands = self.gestures[category]
			for command in sorted(commands):
				treeCom = self.tree.AppendItem(treeCat, command)
				commandInfo = commands[command]
				if wx.version().startswith("4"):
					# for wxPython 4
					self.tree.SetItemData(treeCom, commandInfo)
				else:
					# for wxPython 3
					self.tree.SetItemPyData(treeCom, commandInfo)
				for gesture in commandInfo.gestures:
					treeGes = self.tree.AppendItem(treeCom, self._formatGesture(gesture))
					if wx.version().startswith("4"):
						# for wxPython 4
						self.tree.SetItemData(treeGes, gesture)
					else:
						# for wxPython 3
						self.tree.SetItemPyData(treeGes, gesture)
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
		# #7077: Check if the treeview is still alive.
		try:
			item = self.tree.Selection
		except RuntimeError:
			return
		if wx.version().startswith("4"):
			#for wxPython 4
			data = self.tree.GetItemData(item)
		else:
			# for wxPython 3
			data = self.tree.GetItemPyData(item)
		isCommand = isinstance(data, AllGesturesScriptInfo)
		isGesture = isinstance(data, basestring)
		self.removeButton.Enabled = isGesture

	def onRemove(self, evt):
		treeGes = self.tree.Selection
		if wx.version().startswith("4"):
			# for wxPython 4
			gesture = self.tree.GetItemData(treeGes)
		else:
			# for wxPython 3
			gesture = self.tree.GetItemPyData(treeGes)
		treeCom = self.tree.GetItemParent(treeGes)
		if wx.version().startswith("4"):
			# for wxPython 4
			scriptInfo = self.tree.GetItemData(treeCom)
		else:
			# for wxPython 3
			scriptInfo = self.tree.GetItemPyData(treeCom)
		entry = (gesture, scriptInfo.moduleName, scriptInfo.className, scriptInfo.scriptName)
		self.pendingRemoves.add(entry)
		self.tree.Delete(treeGes)
		scriptInfo.gestures.remove(gesture)
		self.tree.SetFocus()

	def onRemoveAll(self, evt):
		if gui.messageBox(
			# Translators: the label of a message box dialog.
			_("Do you really want to erase all the modification of gesture control that have been made ?"),
			# Translators: the title of a message box dialog.
			_("NVDAExtensionGlobalPlugin add-on - warning"),
			wx.YES|wx.NO|wx.ICON_WARNING) ==wx.NO:
			return
		inputCore.manager.userGestureMap.clear()
		inputCore.manager.userGestureMap.save()
		#self.Destroy()
	
	def onOk(self, evt):
		for gesture, module, className, scriptName in self.pendingRemoves:
			try:
				self.userGestureMap.remove(gesture, module, className, scriptName)
			except ValueError:
				log.warning("passe")
				pass

		if self.pendingRemoves:
			# Only save if there is something to save.
			try:
				self.userGestureMap.save()
			except:
				log.debugWarning("", exc_info=True)
				# Translators: An error displayed when saving user defined input gestures fails.
				gui.messageBox(NVDAString("Error saving user defined gestures - probably read only file system."),
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
			self.userGestureMap.load(os.path.join(globalVars.appArgs.configPath, "gestures.ini"))
		except IOError:
			log.debugWarning("No user gesture map")
			return
		self.addGlobalMap(self.userGestureMap)

	def addResult(self, scriptInfo):
		self.scriptInfo[scriptInfo.cls, scriptInfo.scriptName] = scriptInfo
		try:
			cat = self.results[scriptInfo.category]
		except KeyError:
			cat = self.results[scriptInfo.category] = {}
		cat[scriptInfo.displayName] = scriptInfo
		
	def addGlobalMap(self, gmap):
		for cls, moduleName, className, gesture, scriptName in gmap.getScriptsForAllGestures():
			c = "%s.%s"%(moduleName, className)
			key = (c, gesture)
			if key in self.handledGestures:
				continue
			self.handledGestures.add(key)
			try:
				scriptInfo = self.scriptInfo[c, scriptName]
			except KeyError:
				try:
					script = getattr(cls, "script_%s" % scriptName)
				except AttributeError:
					script = None
				scriptInfo = self.makeNormalScriptInfo(cls, moduleName, className, scriptName, script)
				if not scriptInfo:
					continue
				self.addResult(scriptInfo)
			scriptInfo.gestures.append(gesture)



	def makeNormalScriptInfo(self, cls, moduleName, className, scriptName, script):
		info = AllGesturesScriptInfo(cls, moduleName, className, scriptName)

		category = self.getScriptCategory(cls, script)
		if category is None:
			category = "%s.%s" %(moduleName, className)
		info.category = category
		if script is None:
			if scriptName:
				info.displayName = scriptName
			else:
				info.displayName = _("Deleted gestures")
		else:
			info.displayName = script.__doc__
			if not info.displayName:
				return None
		return info


	def getScriptCategory(self, cls, script):
		try:
			return script.category
		except AttributeError:
			pass
		try:
			return cls.scriptCategory
		except AttributeError:
			pass
		return None


class AllGesturesScriptInfo(inputCore.AllGesturesScriptInfo):
	__slots__ = ("cls", "moduleName", "className", "scriptName", "category", "displayName", "gestures")
	
	def __init__(self, cls, moduleName, className, scriptName):
		self.cls = cls
		self.moduleName = moduleName
		self.className = className
		self.scriptName = scriptName
		self.gestures = []
	
	

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
			except:
				cls = None
			yield cls, moduleName, className, scriptName

	def getScriptsForAllGestures(self):
		"""Get all of the scripts and their gestures.
		@return: The Python class, gesture and script name for each mapping;
			the script name may be C{None} indicating that the gesture should be unbound for this class.
		@rtype: generator of (class, str, str)
		"""
		for gesture in self._map:
			for cls, moduleName, className, scriptName in self.getScriptsForGesture(gesture):
				yield cls, moduleName, className, gesture, scriptName

	