# NVDAExtensionGlobalPlugin/winExplorer/elementListDialog.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2016 - 2021 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import addonHandler
import queueHandler
import speech
import time
import api
import wx
import controlTypes
import gui
import core
import ui
from ..utils import PutWindowOnForeground,  mouseClick, makeAddonWindowTitle
from ..utils.NVDAStrings import NVDAString
from ..utils.py3Compatibility import _unicode
addonHandler.initTranslation()


class ElementListDialog(wx.Dialog):
	_instance = None
	_timer = None
	title = None
	delayTimer = None
	lastTypedKeys = ""
	elementTypes = (
		# Translators: The label of a list item to select the type of object
		# in the Element List Dialog.
		("button", _("Button")),
		# Translators: The label of a list item to select the type of object
		# in the Element List Dialog.
		("checkBox", _("Check box")),
		# Translators: The label of a list item to select the type of object
		# in the Element List Dialog.
		("edit", _("Edit")),
		# Translators: The label of a list item to select the type of object
		# in the Element List Dialog.
		("list", _("List, list's item")),
		# Translators: The label of a list item to select the type of object
		# in the Element List Dialog.
		("treeView", _("Tree view, treeview's item")),
		# Translators: The label of a list item to select the type of object
		# in the Element List Dialog.
		("comboBox", _("ComboBox")),
		# Translators: The label of a list item to select the type of object
		# in the Element List Dialog.
		("tab", _("Tab")),
		# Translators: The label of a list item to select the type of object
		# in the Element List Dialog.
		("slider", _("Slider")),
		# Translators: The label of a list item to select the type of object
		# in the Element List Dialog.
		("link", _("Link")),
		# Translators: The label of a list item to select the type of object
		# in the Element List Dialog.
		("table", _("Table, table's item")),
		# Translators: The label of a list item to select the type of object
		# in the Element List Dialog.
		("menu", _("Menu, menu's item")),
		# Translators: The label of a list item to select the type of object
		# in the Element List Dialog.
		("container", _("Container (Tools bar, panel, application, ...)")),
		# Translators: The label of a list item to select the type of object in
		# the Element List Dialog.
		("text", _("Text")),
		# Translators: The label of a list item to select the type of object
		# in the Element List Dialog.
		("all", _("All"))
		)

	_rolesByType = {
		"button":  (
			controlTypes.ROLE_BUTTON, controlTypes.ROLE_SPINBUTTON,
			controlTypes.ROLE_DROPDOWNBUTTON, controlTypes.ROLE_RADIOBUTTON,
			controlTypes.ROLE_TOGGLEBUTTON, controlTypes.ROLE_MENUBUTTON,
			controlTypes.ROLE_TREEVIEWBUTTON),
		"checkBox":  (controlTypes.ROLE_CHECKBOX,),
		"edit": (controlTypes.ROLE_EDITABLETEXT, controlTypes.ROLE_PASSWORDEDIT,),
		"text": (controlTypes.ROLE_STATICTEXT, controlTypes.ROLE_TEXTFRAME,),
		"list": (controlTypes.ROLE_LIST, controlTypes.ROLE_LISTITEM),
		"comboBox": (controlTypes.ROLE_COMBOBOX,),
		"slider":  (controlTypes.ROLE_SLIDER,),
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
		dialogTitle = _("list of visible items making up the object in the foreground")  # noqa:E501
		title = ElementListDialog.title = makeAddonWindowTitle(dialogTitle)
		super(ElementListDialog, self).__init__(parent, wx.ID_ANY, title)
		self.allObjects = objects
		self.objectTypeHasChanged = True
		self.doGui()

	def doGui(self):
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# Translators: This is the label for a checkBox  in
		# the ElementListDialog dialog.
		labelText = _("Ignore untaggeditems")  # noqa:E501
		self.taggedObjectsCheckBox = sHelper.addItem(wx.CheckBox(
			self, wx.ID_ANY, label=labelText))
		self.taggedObjectsCheckBox.SetValue(True)
		# Translators: This is the label for a listBox  in the ElementListDialog.
		typeLabelText = _("&Type: ")
		self.objectTypesListBox = sHelper.addLabeledControl(
			typeLabelText, wx.ListBox,
			id=wx.ID_ANY,
			choices=tuple(et[1] for et in self.elementTypes))
		self.objectTypesListBox.Select(0)
		# Translators: This is the label for a listBox in the ElementListDialog.
		labelText = _("Elements:")
		self.objectListBox = sHelper.addLabeledControl(
			labelText,  wx.ListBox,
			id=wx.ID_ANY,
			style=wx.LB_SINGLE | wx.LB_ALWAYS_SB | wx.WANTS_CHARS,
			size=(600, 300))
		elementType = self.elementTypes[0][0]
		self.elementsForType = self.getElementsForType(elementType)
		if len(self.elementsForType):
			items = [_unicode(obj[0]) for obj in self.elementsForType]
			self.objectListBox.SetItems(items)
				#[_unicode(obj[0]) for obj in self.elementsForType])
		# the buttons
		bHelper = gui.guiHelper.ButtonHelper(wx.HORIZONTAL)
		# Translators: The label for a button in elements list dialog .
		self.leftClickButton = bHelper.addButton(self, label=_("&Left click"))
		self.leftClickButton.SetDefault()
		# Translators: The label for a button in elements list dialog .
		self.rightClickButton = bHelper.addButton(self, label=_("&Right click"))
		# Translators: The label for a button in elements list dialog .
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
			queueHandler.eventQueue, speech.speakMessage, _(elementType))
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
		for i in range(curIndex+1, len(keyCodes)):
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
		for i in  range(curIndex+1, self.objectListBox .Count):
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
		if len(self.lastTypedKeys) >1:
			# check if we are already on object name starting with typed keys
			curIndex = self.objectListBox .GetSelection()
			if self.objectListBox .GetStringSelection().lower().startswith(self.lastTypedKeys):
				# nothing to do. We are on the good item, just speak it
				wx.CallLater(50, queueHandler.queueFunction, 
					queueHandler.eventQueue, speech.speakMessage, self.objectListBox .GetStringSelection())
				return True
			# set selection on next object  with name starting with lastTypedKeys
			if self.selectNextObject():
				wx.CallLater(50, queueHandler.queueFunction, 
					queueHandler.eventQueue, speech.speakMessage, self.objectListBox .GetStringSelection())
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
				newIndex = index - 1 if index - 1 >= 0 else self.objectTypesListBox.Count - 1  # noqa:E501
			else:
				newIndex = index + 1 if index < self.objectTypesListBox.Count - 1 else 0
			self.objectTypesListBox.SetSelection(newIndex)
			self.objectTypeHasChanged = True
			self.updateObjectsListBox()
			return
		keyCodes = [ord(x[1][0]) for x in self.elementTypes]
		if shiftDown and controlDown :
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
			except:  # noqa:E722
				pass
		try:
			description = obj.description
		except:  # noqa:E722
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
				controlTypes.roleLabels.get(obj.role))
		return name
	def getStateLabel(self, obj):
		states = obj.states
		if controlTypes.STATE_PRESSED in states:
			return controlTypes.stateLabels.get(controlTypes.STATE_PRESSED)
		if controlTypes.STATE_CHECKED in states:
			return controlTypes.stateLabels.get(controlTypes.STATE_CHECKED)
		if controlTypes.STATE_HALFCHECKED in states:
			return controlTypes.stateLabels.get(controlTypes.STATE_HALFCHECKED)
		if obj.role in [controlTypes.ROLE_EDITABLETEXT, ]:
			if controlTypes.STATE_READONLY in states:
				return controlTypes.stateLabels.get(controlTypes.STATE_READONLY )

	def getElementsForType(self, elementType):
		labelAndObjList = []

		for obj in self.allObjects:
			role = obj.role
			if elementType != "all":
				roles = self._rolesByType[elementType]
				if role not in roles:
					continue
			withRole = (elementType == "all") or (len(roles) > 1)
			label = self.getLabel(obj, withRole)
			if label is not None:
				stateLabel = self.getStateLabel(obj)
				if stateLabel:
					label = "%s %s" % (label, stateLabel)
				labelAndObjList.append((label, obj))
		#return sorted(labelAndObjList, key=lambda a: a[0].encode("mbcs"))
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
			speech.speechMode = oldSpeechMode
			mouseClick(obj)
		oldSpeechMode = speech.speechMode
		speech.speechMode = speech.speechMode_off
		itemSelected = self.objectListBox.GetSelection()
		obj = self.elementsForType[itemSelected][1]
		core.callLater(400, callback, obj, oldSpeechMode)
		self.Close()

	def onRightMouseButton(self, event):

		def callback(obj, oldSpeechMode):
			api.processPendingEvents()
			speech.cancelSpeech()
			speech.speechMode = oldSpeechMode
			mouseClick(obj, True)
		oldSpeechMode = speech.speechMode
		speech.speechMode = speech.speechMode_off

		itemSelected = self.objectListBox.GetSelection()
		obj = self.elementsForType[itemSelected][1]
		core.callLater(400, callback, obj, oldSpeechMode)
		self.Close()

	def onNavigatorObjectButton(self,  event):

		def callback(obj, oldspeechMode):
			api.processPendingEvents()
			speech.cancelSpeech()
			speech.speechMode = oldSpeechMode
			api.setNavigatorObject(obj)
			api.moveMouseToNVDAObject(obj)
			speech.speakObject(obj)
		itemSelected = self.objectListBox.GetSelection()
		obj = self.elementsForType[itemSelected][1]
		self.Close()
		oldSpeechMode = speech.speechMode
		speech.speechMode = speech.speechMode_off
		core.callLater(400, callback, obj, oldSpeechMode)

	@classmethod
	def isRunning(cls):
		return cls._instance is not None

	@classmethod
	def run(cls, oParent, objects):
		gui.mainFrame.prePopup()
		d = cls(None, oParent, objects)
		d.CentreOnScreen()
		d.Show()
		gui.mainFrame.postPopup()
		PutWindowOnForeground(d.GetHandle(), 4, 0.1)
