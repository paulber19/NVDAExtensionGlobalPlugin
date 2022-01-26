# NVDAExtensionGlobalPlugin/winExplorer/elementListDialog.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2016 - 2022 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import addonHandler
import queueHandler
import ui
import speech
import time
import api
import wx
import gui
from ..utils import contextHelpEx
try:
	# for nvda version >= 2021.2
	from controlTypes.role import _roleLabels as roleLabels
	from controlTypes.role import Role
	ROLE_EDITABLETEXT = Role.EDITABLETEXT
	from controlTypes.state import _stateLabels as stateLabels
	from controlTypes.state import State
	STATE_PRESSED = State.PRESSED
	STATE_CHECKED = State.CHECKED
	STATE_HALFCHECKED = State.HALFCHECKED
	STATE_READONLY = State.READONLY
except (ModuleNotFoundError, AttributeError):
	from controlTypes import (
		roleLabels, stateLabels,
		ROLE_EDITABLETEXT,
		STATE_PRESSED, STATE_CHECKED, STATE_HALFCHECKED,
		STATE_READONLY)
import core
from ..utils import PutWindowOnForeground, mouseClick, makeAddonWindowTitle, getHelpObj
from ..utils import getSpeechMode, setSpeechMode, setSpeechMode_off
from ..utils.NVDAStrings import NVDAString
addonHandler.initTranslation()

try:
	# for nvda version >= 2021.2
	from controlTypes.role import Role
	_rolesByType = {
		"button": (
			Role.BUTTON, Role.SPINBUTTON,
			Role.DROPDOWNBUTTON, Role.RADIOBUTTON,
			Role.TOGGLEBUTTON, Role.MENUBUTTON,
			Role.TREEVIEWBUTTON),
		"checkBox": (Role.CHECKBOX,),
		"edit": (Role.EDITABLETEXT, Role.PASSWORDEDIT,),
		"text": (Role.STATICTEXT, Role.TEXTFRAME,),
		"list": (Role.LIST, Role.LISTITEM),
		"comboBox": (Role.COMBOBOX,),
		"slider": (Role.SLIDER,),
		"link": (Role.LINK,),
		"table": (
			Role.TABLE, Role.TABLECELL,
			Role.TABLEROW),
		"menu": (
			Role.MENU, Role.MENUITEM,
			Role.RADIOMENUITEM, Role.CHECKMENUITEM,
			Role.MENUBAR, Role.POPUPMENU,
			Role.TEAROFFMENU),
		"container": (
			Role.APPLICATION, Role.DESKTOPPANE,
			Role.DIALOG, Role.DIRECTORYPANE,
			Role.FRAME, Role.GLASSPANE,
			Role.OPTIONPANE, Role.PANE,
			Role.PANEL, Role.TOOLBAR,
			Role.WINDOW),
		"treeView": (Role.TREEVIEW, Role.TREEVIEWITEM),
		"tab": (Role.TAB,)
	}
except (ModuleNotFoundError, AttributeError):
	import controlTypes
	_rolesByType = {
		"button": (
			controlTypes.ROLE_BUTTON, controlTypes.ROLE_SPINBUTTON,
			controlTypes.ROLE_DROPDOWNBUTTON, controlTypes.ROLE_RADIOBUTTON,
			controlTypes.ROLE_TOGGLEBUTTON, controlTypes.ROLE_MENUBUTTON,
			controlTypes.ROLE_TREEVIEWBUTTON),
		"checkBox": (controlTypes.ROLE_CHECKBOX,),
		"edit": (controlTypes.ROLE_EDITABLETEXT, controlTypes.ROLE_PASSWORDEDIT,),
		"text": (controlTypes.ROLE_STATICTEXT, controlTypes.ROLE_TEXTFRAME,),
		"list": (controlTypes.ROLE_LIST, controlTypes.ROLE_LISTITEM),
		"comboBox": (controlTypes.ROLE_COMBOBOX,),
		"slider": (controlTypes.ROLE_SLIDER,),
		"link": (controlTypes.ROLE_LINK,),
		"table": (
			controlTypes.ROLE_TABLE, controlTypes.ROLE_TABLECELL,
			controlTypes.ROLE_TABLEROW),
		"menu": (
			controlTypes.ROLE_MENU, controlTypes.ROLE_MENUITEM,
			controlTypes.ROLE_RADIOMENUITEM, controlTypes.ROLE_CHECKMENUITEM,
			controlTypes.ROLE_MENUBAR, controlTypes.ROLE_POPUPMENU,
			controlTypes.ROLE_TEAROFFMENU),
		"container": (
			controlTypes.ROLE_APPLICATION, controlTypes.ROLE_DESKTOPPANE,
			controlTypes.ROLE_DIALOG, controlTypes.ROLE_DIRECTORYPANE,
			controlTypes.ROLE_FRAME, controlTypes.ROLE_GLASSPANE,
			controlTypes.ROLE_OPTIONPANE, controlTypes.ROLE_PANE,
			controlTypes.ROLE_PANEL, controlTypes.ROLE_TOOLBAR,
			controlTypes.ROLE_WINDOW),
		"treeView": (controlTypes.ROLE_TREEVIEW, controlTypes.ROLE_TREEVIEWITEM),
		"tab": (controlTypes.ROLE_TAB,)
	}


class ElementListDialog(
	contextHelpEx.ContextHelpMixinEx,
	wx.Dialog):
	_instance = None
	# help in the user manual.
	helpObj = getHelpObj("hdr16")
	_timer = None
	title = None
	delayTimer = None
	lastTypedKeys = ""
	elementTypes = (
		# Translators: The label of a list item to select the type of object
		# in the Element List Dialog.
		("button", NVDAString("button").capitalize()),
		# Translators: The label of a list item to select the type of object
		# in the Element List Dialog.
		("checkBox", NVDAString("check box").capitalize()),
		# Translators: The label of a list item to select the type of object
		# in the Element List Dialog.
		("edit", NVDAString("edit").capitalize()),
		# Translators: The label of a list item to select the type of object
		# in the Element List Dialog.
		("list", _("List, list's item")),
		# Translators: The label of a list item to select the type of object
		# in the Element List Dialog.
		("treeView", "%s, %s" % (NVDAString("tree view").capitalize(), NVDAString("tree view item"))),
		# Translators: The label of a list item to select the type of object
		# in the Element List Dialog.
		("comboBox", NVDAString("combo box").capitalize()),
		# Translators: The label of a list item to select the type of object
		# in the Element List Dialog.
		("tab", _("Tab").capitalize()),
		# Translators: The label of a list item to select the type of object
		# in the Element List Dialog.
		("slider", NVDAString("slider").capitalize()),
		# Translators: The label of a list item to select the type of object
		# in the Element List Dialog.
		("link", NVDAString("link").capitalize()),
		# Translators: The label of a list item to select the type of object
		# in the Element List Dialog.
		("table", "%s, %s" % (NVDAString("table").capitalize(), _("table item"))),
		# Translators: The label of a list item to select the type of object
		# in the Element List Dialog.
		("menu", "%s, %s" % (NVDAString("menu").capitalize(), _("menu item"))),
		# Translators: The label of a list item to select the type of object
		# in the Element List Dialog.
		("container", "%s (%s, %s, %s, ...)" % (
			NVDAString("container").capitalize(),
			NVDAString("tool bar"), NVDAString("panel"), NVDAString("application"))),
		# Translators: The label of a list item to select the type of object in
		# the Element List Dialog.
		("text", NVDAString("text").capitalize()),
		# Translators: The label of a list item to select the type of object
		# in the Element List Dialog.
		("all", _("All"))
	)

	def __new__(cls, *args, **kwargs):
		if ElementListDialog._instance is not None:
			return ElementListDialog._instance
		return wx.Dialog.__new__(cls)

	def __init__(self, parent, oParent, objects):
		if ElementListDialog._instance is not None:
			return
		ElementListDialog._instance = self
		self.oParent = oParent
		# Translators: title of dialog box.
		dlgTitle = _("list of visible items making up the object in the foreground")
		title = ElementListDialog.title = makeAddonWindowTitle(dlgTitle)
		super(ElementListDialog, self).__init__(parent, wx.ID_ANY, title)
		self.allObjects = objects
		self.objectTypeHasChanged = True
		self.doGui()

	def doGui(self):
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# Translators: This is the label for a checkBox in
		# the "list of visible items making up the object in the foreground" dialog.
		labelText = _("Ignore untagged items")
		self.taggedObjectsCheckBox = sHelper.addItem(wx.CheckBox(
			self, wx.ID_ANY, label=labelText))
		self.taggedObjectsCheckBox.SetValue(True)
		# Translators: This is the label for a listBox in
		# the "list of visible items making up the object in the foreground" dialog.
		typeLabelText = _("&Type: ")
		self.objectTypesListBox = sHelper.addLabeledControl(
			typeLabelText, wx.ListBox,
			id=wx.ID_ANY,
			choices=tuple(et[1] for et in self.elementTypes))
		self.objectTypesListBox.Select(0)
		# Translators: This is the label for a listBox in
		# the "list of visible items making up the object in the foreground" dialog.
		labelText = _("Elements:")
		self.objectListBox = sHelper.addLabeledControl(
			labelText, wx.ListBox,
			id=wx.ID_ANY,
			style=wx.LB_SINGLE | wx.LB_ALWAYS_SB | wx.WANTS_CHARS,
			size=(600, 300))
		elementType = self.elementTypes[0][0]
		self.elementsForType = self.getElementsForType(elementType)
		if len(self.elementsForType):
			items = [str(obj[0]) for obj in self.elementsForType]
			self.objectListBox.SetItems(items)
		# the buttons
		bHelper = gui.guiHelper.ButtonHelper(wx.HORIZONTAL)
		# Translators: The label for a button in
		# the "list of visible items making up the object in the foreground" dialog.
		self.leftClickButton = bHelper.addButton(self, label=_("&Left click"))
		self.leftClickButton.SetDefault()
		# Translators: The label for a button in
		# the "list of visible items making up the object in the foreground" dialog.
		self.rightClickButton = bHelper.addButton(self, label=_("&Right click"))
		# Translators: The label for a button in
		# the "list of visible items making up the object in the foreground" dialog.
		self.navigatorObjectButton = bHelper.addButton(
			self, label=_("Move &navigator object to it"))
		sHelper.addItem(bHelper)
		bHelper = sHelper.addDialogDismissButtons(
			gui.guiHelper.ButtonHelper(wx.HORIZONTAL))
		closeButton = bHelper.addButton(
			self, id=wx.ID_CLOSE, label=NVDAString("&Close"))
		mainSizer.Add(
			sHelper.sizer, border=gui.guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		# the events
		self.taggedObjectsCheckBox.Bind(
			wx.EVT_CHECKBOX, self.onCheckTaggedObjectsCheckBox)
		self.objectTypesListBox.Bind(wx.EVT_LISTBOX, self.onElementTypeChange)
		self.objectTypesListBox.Bind(wx.EVT_SET_FOCUS, self.onObjectTypeListBoxFocus)
		self.objectListBox.Bind(wx.EVT_SET_FOCUS, self.onObjectListBoxFocus)
		self.objectListBox.Bind(wx.EVT_KEY_DOWN, self.onKeydown)
		self.leftClickButton.Bind(wx.EVT_BUTTON, self.onLeftClickButton)
		self.rightClickButton.Bind(wx.EVT_BUTTON, self.onRightMouseButton)
		self.navigatorObjectButton.Bind(wx.EVT_BUTTON, self.onNavigatorObjectButton)
		closeButton.Bind(wx.EVT_BUTTON, lambda evt: self.Destroy())
		self.SetEscapeId(wx.ID_CLOSE)
		self.objectTypesListBox.SetSelection(0)
		self.objectListBox.SetFocus()
		wx.CallAfter(self.updateObjectsListBox)

	def Destroy(self):
		ElementListDialog._instance = None
		super(ElementListDialog, self).Destroy()

	def updateObjectsListBox(self):
		index = self.objectTypesListBox.GetSelection()
		elementType = self.elementTypes[index][1]
		queueHandler.queueFunction(
			queueHandler.eventQueue, ui.message, _(elementType))
		queueHandler.queueFunction(
			queueHandler.eventQueue, self.onElementTypeChange, None)
		wx.CallLater(1000, self._onObjectListBoxFocus)

	def selectElementType(self, keyCode):
		keyCodes = [x[1][0].lower() for x in self.elementTypes]
		key = chr(keyCode).lower()
		if key not in keyCodes:
			return False
		curIndex = self.objectTypesListBox.GetSelection()
		index = None
		for i in range(curIndex + 1, len(keyCodes)):
			k = keyCodes[i]
			if k == key:
				index = i
				break

		if index is None:
			for i in range(0, curIndex):
				k = keyCodes[i]
				if k == key:
					index = i
					break

		if index is not None:
			self.objectTypesListBox.SetSelection(index)
			self.objectTypeHasChanged = True
			self.updateObjectsListBox()
			return True
		return False

	def selectNextObject(self):
		if self.objectListBox .Count <= 1:
			return False
		curIndex = self.objectListBox .GetSelection()
		index = None
		for i in range(curIndex + 1, self.objectListBox .Count):
			name = self.objectListBox .GetString(i)
			if name.lower().startswith(self.lastTypedKeys):
				index = i
				break
		if index is None:
			for i in range(0, curIndex):
				name = self.objectListBox .GetString(i)
				if name.lower().startswith(self.lastTypedKeys):
					index = i
					break
		if index is not None:
			self.objectListBox .SetSelection(index)
			return True
		return False

	def manageKeyInput(self, keyCode):
		curTime = time.time_ns() // 1_000_000
		if not hasattr(self, "lastKeyDownTime"):
			self.lastKeyDownTime = 0
			self.lastTypedKeys = ""
		if not (30 <= keyCode <= 255):
			# no alphanumeric character, so  ignore it
			self.lastTypedKeys = ""
			return False
		key = chr(keyCode).lower()
		delayBetweenKeys = curTime - self.lastKeyDownTime
		self.lastKeyDownTime = curTime
		if delayBetweenKeys > 500:
			self.lastTypedKeys = key
			return False
		self.lastTypedKeys += key
		if len(self.lastTypedKeys) > 1:
			# check if we are already on object name starting with typed keys
			if self.objectListBox .GetStringSelection().lower().startswith(self.lastTypedKeys):
				# nothing to do. We are on the good item, just speak it
				wx.CallLater(
					50,
					queueHandler.queueFunction,
					queueHandler.eventQueue,
					ui.message,
					self.objectListBox .GetStringSelection())
				return True
			# set selection on next object  with name starting with lastTypedKeys
			if self.selectNextObject():
				wx.CallLater(
					50,
					queueHandler.queueFunction,
					queueHandler.eventQueue,
					ui.message,
					self.objectListBox .GetStringSelection())
			return True
		return False

	def onKeydown(self, evt):
		keyCode = evt.GetKeyCode()
		controlDown = evt.ControlDown()
		shiftDown = evt.ShiftDown()
		if self.delayTimer is not None:
			self.delayTimer.Stop()
			self.delayTimer = None
		if keyCode == wx.WXK_TAB:
			if shiftDown:
				wx.Window.Navigate(self.objectListBox, wx.NavigationKeyEvent.IsBackward)
			else:
				wx.Window.Navigate(self.objectListBox, wx.NavigationKeyEvent.IsForward)
			return
		if keyCode == 13:
			if self.leftClickButton.Enable:
				self.onLeftClickButton(None)
			return
		if keyCode in [314, 316]:  # leftArrow or rightArrow
			# change type of objects.
			index = self.objectTypesListBox.GetSelection()
			if keyCode == 314:
				newIndex = index - 1 if index - 1 >= 0 else self.objectTypesListBox.Count - 1
			else:
				newIndex = index + 1 if index < self.objectTypesListBox.Count - 1 else 0
			self.objectTypesListBox.SetSelection(newIndex)
			self.objectTypeHasChanged = True
			self.updateObjectsListBox()
			return
		if shiftDown and controlDown:
			if self.selectElementType(keyCode):
				return
			evt.Skip()
			return
		if self.manageKeyInput(keyCode):
			return
		evt.Skip()

	def onObjectTypeListBoxFocus(self, evt):
		self.sayNumberOfElements()
		self.objectTypeHasChanged = False

	def onCheckTaggedObjectsCheckBox(self, evt):
		self.onElementTypeChange(evt)

	def getLabel(self, obj, withRole=False):
		taggedObjectsFilter = self.taggedObjectsCheckBox.GetValue()
		try:
			name = obj.name
		except AttributeError:
			name = None
		if name is None and hasattr(obj, "IAccessibleObject"):
			try:
				name = obj.IAccessibleObject.accName(0).strip()
			except Exception:
				pass
		try:
			description = obj.description
		except Exception:
			description = None
		if name is not None and name == description:
			description = None
		if name is not None:
			name = name.strip()
		if name == "":
			name = None
		if description is not None:
			description = description.strip()
		if description == "":
			description = None
		if name is None and description is None and taggedObjectsFilter:
			return None
		name = _("No label") if name is None else name
		if description is not None:
			name = "%s, %s" % (name, description)
		if name[-1] in [",", ".", ";", ":"]:
			name = name[:-1]

		if withRole:
			name = "%s, %s" % (
				name,
				roleLabels.get(obj.role))
		return name

	def getStateLabel(self, obj):
		states = obj.states
		if STATE_PRESSED in states:
			return stateLabels.get(STATE_PRESSED)
		if STATE_CHECKED in states:
			return stateLabels.get(STATE_CHECKED)
		if STATE_HALFCHECKED in states:
			return stateLabels.get(STATE_HALFCHECKED)
		if obj.role in [ROLE_EDITABLETEXT, ]:
			if STATE_READONLY in states:
				return stateLabels.get(STATE_READONLY)

	def getElementsForType(self, elementType):
		labelAndObjList = []

		for obj in self.allObjects:
			role = obj.role
			if elementType != "all":
				roles = _rolesByType[elementType]
				if role not in roles:
					continue
			withRole = (elementType == "all") or (len(roles) > 1)
			label = self.getLabel(obj, withRole)
			if label is not None:
				stateLabel = self.getStateLabel(obj)
				if stateLabel:
					label = "%s %s" % (label, stateLabel)
				labelAndObjList.append((label, obj))
		return sorted(labelAndObjList, key=lambda a: a[0])

	def sayNumberOfElements(self):

		def callback(count):
			self._timer = None
			# Check if the listbox is still alive.
			try:
				if not self.objectTypesListBox.HasFocus() and\
					not self.objectListBox.HasFocus():
					return
			except RuntimeError:
				return
			if count:
				msg = _("%s elements") % str(count) if count > 1 else _("One element")
				ui.message(msg)
			else:
				ui.message(_("no element"))
		if self._timer is not None:
			self._timer.Stop()
		self._timer = core.callLater(200, callback, self.objectListBox.Count)

	def updateButtons(self, enable=True):
		if enable:
			self.leftClickButton.Enable()
			self.leftClickButton.SetDefault()
			self.rightClickButton.Enable()
			self.navigatorObjectButton.Enable()
		else:
			self.leftClickButton.Disable()
			self.rightClickButton.Disable()
			self.navigatorObjectButton.Disable()

	def onObjectListBoxFocus(self, evt):
		self._onObjectListBoxFocus()

	def _onObjectListBoxFocus(self):
		if self.objectListBox.GetCount() == 0:
			self.updateButtons(False)
		else:
			if self.objectTypeHasChanged:
				self.objectListBox.Select(0)
			self.updateButtons(True)
			self.objectTypeHasChanged = False

	def onElementTypeChange(self, evt):
		index = self.objectTypesListBox.GetSelection()
		elementType = self.elementTypes[index][0]
		self.elementsForType = self.getElementsForType(elementType)
		self.objectListBox.Clear()
		self.objectListBox.SetItems([obj[0] for obj in self.elementsForType])
		self.sayNumberOfElements()
		self.objectTypeHasChanged = True

	def onLeftClickButton(self, event):

		def callback(obj, oldSpeechMode):
			api.processPendingEvents()
			speech.cancelSpeech()
			setSpeechMode(oldSpeechMode)
			mouseClick(obj)
		oldSpeechMode = getSpeechMode()
		setSpeechMode_off()
		itemSelected = self.objectListBox.GetSelection()
		obj = self.elementsForType[itemSelected][1]
		core.callLater(400, callback, obj, oldSpeechMode)
		self.Close()

	def onRightMouseButton(self, event):
		def callback(obj, oldSpeechMode):
			api.processPendingEvents()
			speech.cancelSpeech()
			setSpeechMode(oldSpeechMode)
			mouseClick(obj, True)
		oldSpeechMode = getSpeechMode()
		setSpeechMode_off()
		itemSelected = self.objectListBox.GetSelection()
		obj = self.elementsForType[itemSelected][1]
		core.callLater(400, callback, obj, oldSpeechMode)
		self.Close()

	def onNavigatorObjectButton(self, event):
		def callback(obj, oldspeechMode):
			api.processPendingEvents()
			speech.cancelSpeech()
			setSpeechMode(oldSpeechMode)
			api.setNavigatorObject(obj)
			api.moveMouseToNVDAObject(obj)
			speech.speakObject(obj)
		itemSelected = self.objectListBox.GetSelection()
		obj = self.elementsForType[itemSelected][1]
		self.Close()
		oldSpeechMode = getSpeechMode()
		setSpeechMode_off()
		core.callLater(400, callback, obj, oldSpeechMode)

	@classmethod
	def run(cls, oParent, objects):
		gui.mainFrame.prePopup()
		d = cls(None, oParent, objects)
		d.CentreOnScreen()
		d.Show()
		gui.mainFrame.postPopup()
		PutWindowOnForeground(d.GetHandle(), 4, 0.1)
