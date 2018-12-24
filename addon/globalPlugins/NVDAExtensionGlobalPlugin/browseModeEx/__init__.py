# NVDAExtensionGlobalPlugin/browseModeEx/__init__.py
#A part of NVDAExtensionGlobalPlugin add-on
#Copyright (C) 2016-2018 paulber19
#This file is covered by the GNU General Public License.


import addonHandler
addonHandler.initTranslation()
import os
import NVDAObjects.UIA.edge
import NVDAObjects.IAccessible.MSHTML
import NVDAObjects.IAccessible.mozilla
import NVDAObjects.IAccessible.chromium
import browseMode
import documentBaseEx
import core
from inputCore import SCRCAT_BROWSEMODE
import wx
import collections
import gui
from scriptHandler import isScriptWaiting, getLastScriptRepeatCount, willSayAllResume
import tones
import winsound
from ..__init__ import GB_taskTimer
from ..utils.NVDAStrings import NVDAString
import queueHandler
import speech
import ui
import textInfos
import itertools
import api
import config
import controlTypes
import NVDAObjectsIAccessible
from ..settings import toggleLoopInNavigationModeOption


# Add new quick navigation keys and scripts.
qn = browseMode.BrowseModeTreeInterceptor.addQuickNav
qn("paragraph", key="p", 
	# Translators: Input help message for a quick navigation command in browse mode.
	nextDoc=_("moves to the next paragraph"), 
	# Translators: Message presented when the browse mode element is not found.
	nextError=_("no next paragraph"),
	# Translators: Input help message for a quick navigation command in browse mode.
	prevDoc=_("moves to the previous paragraph"), 
	# Translators: Message presented when the browse mode element is not found.
	prevError=_("no previous paragraph"), readUnit=textInfos.UNIT_PARAGRAPH)
qn("division", key="y", 
	# Translators: Input help message for a quick navigation command in browse mode.
	nextDoc=_("moves to the next division"), 
	# Translators: Message presented when the browse mode element is not found.
	nextError=_("no next division"),
	# Translators: Input help message for a quick navigation command in browse mode.
	prevDoc=_("moves to the previous division"), 
	# Translators: Message presented when the browse mode element is not found.
	prevError=_("no previous division"), readUnit=textInfos.UNIT_LINE)
qn("mainLandmark", key=";", 
	# Translators: Input help message for a quick navigation command in browse mode.
	nextDoc=_("moves to the next main landmark"), 
	# Translators: Message presented when the browse mode element is not found.
	nextError=_("no next main landmark"),
	# Translators: Input help message for a quick navigation command in browse mode.
	prevDoc=_("moves to the previous main landmark"), 
	# Translators: Message presented when the browse mode element is not found.
	prevError=_("no previous main landmark"), readUnit=textInfos.UNIT_LINE)

qn("clickable", key=":",
	# Translators: Input help message for a quick navigation command in browse mode.
	nextDoc=_("moves to the next clickable element"),
	# Translators: Message presented when the browse mode element is not found.
	nextError=_("no next clickable element"),
	# Translators: Input help message for a quick navigation command in browse mode.
	prevDoc=_("moves to the previous clickable element"),
	# Translators: Message presented when the browse mode element is not found.
	prevError=_("no previous clickable element"),
	readUnit=textInfos.UNIT_PARAGRAPH)
del qn


from cursorManager import CursorManager
class CursorManagerEx(CursorManager):
	# we want to ear symbols and punctuation when moving by  word
	def _caretMovementScriptHelper(self,gesture,unit,direction=None,posConstant=textInfos.POSITION_SELECTION,posUnit=None,posUnitEnd=False,extraDetail=False,handleSymbols=False):
		curLevel = config.conf["speech"]["symbolLevel"]
		if unit == textInfos.UNIT_WORD :
			from ..settings import _addonConfigManager
			symbolLevelOnWordCaretMovement = _addonConfigManager .getSymbolLevelOnWordCaretMovement()
			if symbolLevelOnWordCaretMovement  is not None:
				config.conf["speech"]["symbolLevel"] = symbolLevelOnWordCaretMovement
		super(CursorManagerEx, self)._caretMovementScriptHelper(gesture,unit,direction,posConstant,posUnit,posUnitEnd,extraDetail,handleSymbols)

		config.conf["speech"]["symbolLevel"] = curLevel

class BrowseModeDocumentTreeInterceptorEx (documentBaseEx.DocumentWithTableNavigationEx,CursorManagerEx, browseMode.BrowseModeDocumentTreeInterceptor):
	_myGestureMap = {
		"kb(desktop):nvda+a" : "reportDocumentConstantIdentifier",
		"kb(laptop):nvda+shift+a" : "reportDocumentConstantIdentifier",
		}

	def __init__(self,rootNVDAObject):
		super(BrowseModeDocumentTreeInterceptorEx ,self).__init__(rootNVDAObject)
		self.bindGestures(BrowseModeDocumentTreeInterceptorEx._myGestureMap )
	


	def script_reportDocumentConstantIdentifier(self, gesture):
		global GB_taskTimer
		def callback(toClip = False):
			global GB_taskTimer
			GB_taskTimer = None
			text = self._get_documentConstantIdentifier()
			if not text: return
			if not toClip:
							ui.message(text)
			else:
				if api.copyToClip(text):
					msg = text
					if len(text) >35:
						l = text[:35].split("/")
						l[-1] = "..."
						msg = "/".join(l)
					ui.message(msg)
					# Translators: message presented when the text is copied to the clipboard.
					speech.speakMessage(_("Copied to clipboard"))
				else:
					# Translators: message presented when the text cannot be copied to the clipboard.
					speech.speakMessage(_("Cannot copy to clipboard"))
		
		if GB_taskTimer is not None:
			GB_taskTimer.Stop()
			GB_taskTimer = None

		if getLastScriptRepeatCount() == 0:
			GB_taskTimer = core.callLater(250, callback, False)
		else:
			callback(True)
			
	# Translators: Input help mode message for report Document Constant Identifier command.
	script_reportDocumentConstantIdentifier.__doc__ = _("Report document 's address (URL). Twice: copy it to clipboard")
	script_reportDocumentConstantIdentifier.category=SCRCAT_BROWSEMODE


	def _quickNavScript(self,gesture, itemType, direction, errorMessage, readUnit):
		if itemType=="notLinkBlock":
			iterFactory=self._iterNotLinkBlock
		else:
			iterFactory=lambda direction,info: self._iterNodesByType(itemType,direction,info)
		info=self.selection
		try:
			item = next(iterFactory(direction, info))
		except NotImplementedError:
			# Translators: a message when a particular quick nav command is not supported in the current document.
			ui.message(NVDAString("Not supported in this document"))
			return
		except StopIteration:
			if not toggleLoopInNavigationModeOption(False):
				ui.message(errorMessage)
				return
				
			# return to the top or bottom of page and continue search
			if direction == "previous":
				info=api.getReviewPosition().obj.makeTextInfo(textInfos.POSITION_LAST)
				self._set_selection(info, reason="quickNav")
				# Translators: message to the user which indicates the return to  the bottom of the page.
				msg = _("Return to bottom of page")
			else:
				info = None
				# Translators: message to the user which indicates the return to the top of the page.
				msg = _("Return to top of page")
			try:
				item = next(iterFactory(direction, info))
			except:
				ui.message(errorMessage)
				return
			ui.message(msg)
			winsound.PlaySound("default",1)
		item.moveTo()
		if not gesture or not willSayAllResume(gesture):
			item.report(readUnit=readUnit)
from ..utils import runInThread
class ElementsListDialogEx(wx.Dialog):
	ELEMENT_TYPES = (
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("link", _("Link")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("heading", _("Heading")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("formField", _("Form field")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("button", _("Button")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("landmark", _("Landmark")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("radioButton",_("Radio button")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("paragraph", _("Paragraph")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("frame",_("Frame")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("division",_("Division")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("checkBox", _("Check box")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("comboBox",_("Combo box")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("table", _("Table")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("blockQuote", _("Blocquote")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("edit",_("Edit")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("list",_("List")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("listItem",_("List item")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("anchor",_("Anchor")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("graphic", _("Graphic")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("embeddedObject", _("Embedded object")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("separator", _("Separator")),
		)
	
	Element = collections.namedtuple("Element", ("item", "parent"))
	lastSelectedElementType=0
	_timer = None
	
	def __init__(self, document):
		self.document = document
		# Translators: The title of the browse mode Elements List dialog.
		super(ElementsListDialogEx, self).__init__(gui.mainFrame, wx.ID_ANY, NVDAString("Elements List"))
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		contentsSizer = wx.BoxSizer(wx.VERTICAL)
		childSizer=wx.BoxSizer(wx.VERTICAL)
		# Translators: The label of a list of items to select the type of element
		# in the browse mode Elements List dialog.

		childLabel=wx.StaticText(self,wx.ID_ANY,label= NVDAString("&Type:") , style =wx.ALIGN_CENTRE )
		childSizer.Add(childLabel, )
		self.childListBox =wx.ListBox(self,wx.ID_ANY,name= "TypeName" ,choices=tuple(et[1] for et in self.ELEMENT_TYPES),  style = wx.LB_SINGLE,size= (596,130))
		if self.childListBox.GetCount():
			self.childListBox.SetSelection(self.lastSelectedElementType)
		self.childListBox.Bind(wx.EVT_LISTBOX, self.onElementTypeChange)
		self.childListBox.Bind(wx.EVT_SET_FOCUS, self.onChildBoxFocus)
		childSizer.Add(self.childListBox)
		contentsSizer.Add(childSizer, flag=wx.EXPAND)
		contentsSizer.AddSpacer(gui.guiHelper.SPACE_BETWEEN_VERTICAL_DIALOG_ITEMS)

		self.tree = wx.TreeCtrl(self, size=wx.Size(500, 600), style=wx.TR_HAS_BUTTONS | wx.TR_HIDE_ROOT | wx.TR_LINES_AT_ROOT | wx.TR_SINGLE | wx.TR_EDIT_LABELS)
		self.tree.Bind(wx.EVT_SET_FOCUS, self.onTreeSetFocus)
		self.tree.Bind(wx.EVT_CHAR, self.onTreeChar)
		self.tree.Bind(wx.EVT_TREE_BEGIN_LABEL_EDIT, self.onTreeLabelEditBegin)
		self.tree.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.onTreeLabelEditEnd)
		self.treeRoot = self.tree.AddRoot("root")
		contentsSizer.Add(self.tree,flag=wx.EXPAND)
		contentsSizer.AddSpacer(gui.guiHelper.SPACE_BETWEEN_VERTICAL_DIALOG_ITEMS)

		# Translators: The label of an editable text field to filter the elements
		# in the browse mode Elements List dialog.
		filterText = NVDAString("Filt&er by:")
		labeledCtrl = gui.guiHelper.LabeledControlHelper(self, filterText, wx.TextCtrl)
		self.filterEdit = labeledCtrl.control
		self.filterEdit.Bind(wx.EVT_TEXT, self.onFilterEditTextChange)
		contentsSizer.Add(labeledCtrl.sizer)
		contentsSizer.AddSpacer(gui.guiHelper.SPACE_BETWEEN_VERTICAL_DIALOG_ITEMS)
		
		bHelper = gui.guiHelper.ButtonHelper(wx.HORIZONTAL)
		# Translators: The label of a button to activate an element
		# in the browse mode Elements List dialog.
		self.activateButton = bHelper.addButton(self, label= NVDAString("&Activate"))
		self.activateButton.Bind(wx.EVT_BUTTON, lambda evt: self.onAction(True))
		
		# Translators: The label of a button to move to an element
		# in the browse mode Elements List dialog.
		self.moveButton = bHelper.addButton(self, label= NVDAString("&Move to"))
		self.moveButton.Bind(wx.EVT_BUTTON, lambda evt: self.onAction(False))
		bHelper.addButton(self, id=wx.ID_CANCEL)

		contentsSizer.Add(bHelper.sizer, flag=wx.ALIGN_RIGHT)
		mainSizer.Add(contentsSizer, border=gui.guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)

		self.tree.SetFocus()
		# delay  initList to ear the title of window
		wx.CallLater(200, self.initElementType, self.ELEMENT_TYPES[self.lastSelectedElementType][0])
		self.CentreOnScreen()
	
	def onElementTypeChange(self, evt):
		if self._timer:
			self._timer.Stop()
		elementType=evt.GetInt()
		# We need to make sure this gets executed after the focus event.
		# Otherwise, NVDA doesn't seem to get the event.
		#queueHandler.queueFunction(queueHandler.eventQueue, self.initElementType, self.ELEMENT_TYPES[elementType][0])
		wx.CallLater(200, self.initElementType, self.ELEMENT_TYPES[elementType][0])
		self.lastSelectedElementType=elementType
	
	def initElementType(self, elType):
		if elType in ("link","button", "radioButton", "checkBox"):
			# Links, buttons  , radio button, check box can be activated.
			self.activateButton.Enable()
			self.SetAffirmativeId(self.activateButton.GetId())
		else:
			# No other element type can be activated.
			self.activateButton.Disable()
			self.SetAffirmativeId(self.moveButton.GetId())

		# Gather the elements of this type.
		th = runInThread.RepeatBeep(delay = 1.5, beep = (200,200) )
		th.start()
		self._elements = []
		self._initialElement = None

		parentElements = []
		isAfterSelection=False
		maxItemNumber = -1
		try:
			for item in self.document._iterNodesByType(elType):
				if maxItemNumber == 0: break
				maxItemNumber = maxItemNumber -1  if maxItemNumber >= 0 else maxItemNumber
				# Find the parent element, if any.
				for parent in reversed(parentElements):
					if item.isChild(parent.item):
						break
					else:
						# We're not a child of this parent, so this parent has no more children and can be removed from the stack.
						parentElements.pop()
				else:
					# No parent found, so we're at the root.
					# Note that parentElements will be empty at this point, as all parents are no longer relevant and have thus been removed from the stack.
					parent = None
	
				element=self.Element(item,parent)
				self._elements.append(element)
	
				if not isAfterSelection:
					isAfterSelection=item.isAfterSelection
					if not isAfterSelection:
						# The element immediately preceding or overlapping the caret should be the initially selected element.
						# Since we have not yet passed the selection, use this as the initial element. 
						try:
							self._initialElement = self._elements[-1]
						except IndexError:
							# No previous element.
							pass
	
				# This could be the parent of a subsequent element, so add it to the parents stack.
				parentElements.append(element)
		except:
			pass
		# Start with no filtering.
		self.filterEdit.ChangeValue("")
		self.filter("", newElementType=True)
		self.sayNumberOfElements()
		th.stop()

	def Destroy(self):
		if self._timer is not None:
			self._timer .Stop()
			self._timer  = None
		super(ElementsListDialogEx, self).Destroy()	
		
	def sayNumberOfElements(self):
		def callback (count):
			self._timer = None
			if not self.childListBox.HasFocus(): return
			if count:
				# Translators: message to the user to report number of elements.
				msg = _("%s elements") %str(count) if count > 1 else _("One element")
				queueHandler.queueFunction(queueHandler.eventQueue, speech.speakMessage, msg)
			else:
				# Translators: message to the user when there is no element.
				queueHandler.queueFunction(queueHandler.eventQueue, speech.speakMessage, _("no element"))
		if self._timer:
			self._timer.Stop()
		
		self._timer = wx.CallLater(600,callback, self.tree.Count) 
	def onChildBoxFocus(self, evt):
		self.sayNumberOfElements()		

	def filter(self, filterText, newElementType=False):
		# If this is a new element type, use the element nearest the cursor.
		# Otherwise, use the currently selected element.

		try:
			if wx.version().startswith("4"):
				# for wxPython 4
				defaultElement = self._initialElement if newElementType else self.tree.GetItemData(self.tree.GetSelection())
			else:
				# for wxPython 3
				defaultElement = self._initialElement if newElementType else self.tree.GetItemPyData(self.tree.GetSelection())
		except:
			defaultElement = self._initialElement
		# Clear the tree.
		self.tree.DeleteChildren(self.treeRoot)

		# Populate the tree with elements matching the filter text.
		elementsToTreeItems = {}
		defaultItem = None
		matched = False
		#Do case-insensitive matching by lowering both filterText and each element's text.
		filterText=filterText.lower()
		for element in self._elements:
			label=element.item.label
			if filterText and filterText not in label.lower():
				continue
			matched = True
			parent = element.parent
			if parent:
				parent = elementsToTreeItems.get(parent)
			item = self.tree.AppendItem(parent or self.treeRoot, label)
			if wx.version().startswith("4"):
				# for wxPython 4
				self.tree.SetItemData(item, element)
			else:
				#for wxPython 3
				self.tree.SetItemPyData(item, element)
			elementsToTreeItems[element] = item
			if element == defaultElement:
				defaultItem = item

		self.tree.ExpandAll()

		if not matched:
			# No items, so disable the buttons.
			self.activateButton.Disable()
			self.moveButton.Disable()
			return

		# If there's no default item, use the first item in the tree.
		self.tree.SelectItem(defaultItem or self.tree.GetFirstChild(self.treeRoot)[0])
		# Enable the button(s).
		# If the activate button isn't the default button, it is disabled for this element type and shouldn't be enabled here.
		if self.AffirmativeId == self.activateButton.Id:
			self.activateButton.Enable()
		self.moveButton.Enable()

	def onTreeSetFocus(self, evt):
		# Start with no search.
		self._searchText = ""
		self._searchCallLater = None
		evt.Skip()

	def onTreeChar(self, evt):
		key = evt.KeyCode

		if key == wx.WXK_RETURN:
			# The enter key should be propagated to the dialog and thus activate the default button,
			# but this is broken (wx ticket #3725).
			# Therefore, we must catch the enter key here.
			# Activate the current default button.
			evt = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, wx.ID_ANY)
			button = self.FindWindowById(self.AffirmativeId)
			if button.Enabled:
				button.ProcessEvent(evt)
			else:
				wx.Bell()

		elif key == wx.WXK_F2:
			item=self.tree.GetSelection()
			if item:
				if wx.version().startswith("4"):
					# for wxPython 4
					selectedItemType=self.tree.GetItemData(item).item
				else:
					# wxPython 3
					selectedItemType=self.tree.GetItemPyData(item).item
				self.tree.EditLabel(item)
				evt.Skip()

		elif key >= wx.WXK_START or key == wx.WXK_BACK:
			# Non-printable character.
			self._searchText = ""
			evt.Skip()

		else:
			# Search the list.
			# We have to implement this ourselves, as tree views don't accept space as a search character.
			char = unichr(evt.UnicodeKey).lower()
			# IF the same character is typed twice, do the same search.
			if self._searchText != char:
				self._searchText += char
			if self._searchCallLater:
				self._searchCallLater.Restart()
			else:
				self._searchCallLater = wx.CallLater(1000, self._clearSearchText)
			self.search(self._searchText)

	def onTreeLabelEditBegin(self,evt):
		item=self.tree.GetSelection()
		if wx.version().startswith("4"):
			#  for wxPython 4
			selectedItemType = self.tree.GetItemData(item).item
		else:
			# for wxPython 3
			selectedItemType = self.tree.GetItemPyData(item).item
		if not selectedItemType.isRenameAllowed:
			evt.Veto()

	def onTreeLabelEditEnd(self,evt):
			selectedItemNewName=evt.GetLabel()
			item=self.tree.GetSelection()

			if wx.version().startswith("4"):
				# for wxPython 4
				selectedItemType = self.tree.GetItemData(item).item
			else:
				# for wxPython 3
				selectedItemType = self.tree.GetItemPyData(item).item
			selectedItemType.rename(selectedItemNewName)

	def _clearSearchText(self):
		self._searchText = ""

	def search(self, searchText):
		item = self.tree.GetSelection()
		if not item:
			# No items.
			return

		# First try searching from the current item.
		# Failing that, search from the first item.
		items = itertools.chain(self._iterReachableTreeItemsFromItem(item), self._iterReachableTreeItemsFromItem(self.tree.GetFirstChild(self.treeRoot)[0]))
		if len(searchText) == 1:
			# If only a single character has been entered, skip (search after) the current item.
			next(items)

		for item in items:
			if self.tree.GetItemText(item).lower().startswith(searchText):
				self.tree.SelectItem(item)
				return

		# Not found.
		wx.Bell()

	def _iterReachableTreeItemsFromItem(self, item):
		while item:
			yield item

			childItem = self.tree.GetFirstChild(item)[0]
			if childItem and self.tree.IsExpanded(item):
				# Has children and is reachable, so recurse.
				for childItem in self._iterReachableTreeItemsFromItem(childItem):
					yield childItem

			item = self.tree.GetNextSibling(item)

	def onFilterEditTextChange(self, evt):
		self.filter(self.filterEdit.GetValue())
		evt.Skip()

	def onAction(self, activate):
		self.Close()
		# Save off the last selected element type on to the class so its used in initialization next time.
		self.__class__.lastSelectedElementType=self.lastSelectedElementType
		item = self.tree.GetSelection()
		if wx.version().startswith("4"):
			# for wxPython 4
			item = self.tree.GetItemData(item).item
		else:
			#for  wxPython 3
			item = self.tree.GetItemPyData(item).item
		if activate:
			item.activate()
		else:
			def move():
				speech.cancelSpeech()
				item.moveTo()
				item.report()
			# We must use core.callLater rather than wx.CallLater to ensure that the callback runs within NVDA's core pump.
			# If it didn't, and it directly or indirectly called wx.Yield, it could start executing NVDA's core pump from within the yield, causing recursion.
			core.callLater(100, move)

class GeckoElementsListDialog(ElementsListDialogEx):
	ELEMENT_TYPES = (
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("link", _("Link")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("heading", _("Heading")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("formField", _("Form field")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("button", _("Button")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("landmark", _("Landmark")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("radioButton",_("Radio button")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("paragraph", _("Paragraph")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("frame",_("Frame")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("division",_("Division")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("checkBox", _("Check box")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("comboBox",_("Combo box")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("table", _("Table")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("blockQuote", _("Blocquote")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("edit",_("Edit")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("list",_("List")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("listItem",_("List item")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("anchor",_("Anchor")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("graphic", _("Graphic")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("embeddedObject", _("Embedded object")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("separator", _("Separator")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("clickable", _("Clickable")),
		)
	
	Element = collections.namedtuple("Element", ("item", "parent"))
	lastSelectedElementType=0
	_timer = None



def chooseNVDAObjectOverlayClasses(obj, clsList):
	#print "clsList: %s" %clsList
	if NVDAObjects.UIA.edge.EdgeHTMLRoot in clsList:
		from NVDAObjectsUIA import EdgeHTMLRootEx
		clsList[clsList.index(NVDAObjects.UIA.edge.EdgeHTMLRoot)] = EdgeHTMLRootEx
	elif NVDAObjects.IAccessible.MSHTML.MSHTML in clsList:
		clsList[clsList.index(NVDAObjects.IAccessible.MSHTML.MSHTML)] = NVDAObjectsIAccessible.NVDAObjectMSHTMLEx
	elif NVDAObjects.IAccessible.mozilla.Document in clsList:
		#print "clsList: %s" %clsList
		clsList[clsList.index(NVDAObjects.IAccessible.mozilla.Document)] = NVDAObjectsIAccessible.NVDAObjectMozillaDocumentEx
	elif NVDAObjects.IAccessible.chromium.Document in clsList:
		clsList[clsList.index(NVDAObjects.IAccessible.chromium.Document)] = NVDAObjectsIAccessible.ChromiumDocument
		