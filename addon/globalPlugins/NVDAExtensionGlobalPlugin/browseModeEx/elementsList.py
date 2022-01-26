# globalPlugins\NVDAExtensionGlobalPlugin\browseModeEx\elementsListDialog.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2016 - 2022 paulber19
# This file is covered by the GNU General Public License.


import addonHandler

import core
import wx
import collections
import gui
import queueHandler
import ui
import speech
import itertools
from ..utils.NVDAStrings import NVDAString
from ..utils import runInThread
from ..utils import contextHelpEx

addonHandler.initTranslation()


class ElementsListDialogEx(
	contextHelpEx.ContextHelpMixinEx,
	wx.Dialog):
	# help id in the user manual.
	helpId = "hdr5"

	ELEMENT_TYPES = (
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("link", NVDAString("link").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("heading", NVDAString("heading").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("formField", _("Form field")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("button", NVDAString("button").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("landmark", NVDAString("landmark").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("radioButton", NVDAString("radio button".capitalize())),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("paragraph", NVDAString("paragraph").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("frame", NVDAString("frame").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("division", NVDAString("division").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("checkBox", NVDAString("check box").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("comboBox", NVDAString("combo box").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("table", NVDAString("table").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("blockQuote", NVDAString("block quote").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("edit", NVDAString("edit").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("list", NVDAString("list").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("listItem", NVDAString("list item").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("anchor", _("Anchor")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("graphic", NVDAString("graphic").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("embeddedObject", NVDAString("embedded object").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("separator", NVDAString("separator").capitalize()),
	)
	Element = collections.namedtuple("Element", ("item", "parent"))
	lastSelectedElementType = 0
	_timer = None

	def __init__(self, document):
		self.document = document
		# Translators: The title of the browse mode Elements List dialog.
		self.dialogTitle = NVDAString("Elements List")
		super(ElementsListDialogEx, self).__init__(
			gui.mainFrame, wx.ID_ANY, title=self.dialogTitle)
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		contentsSizer = wx.BoxSizer(wx.VERTICAL)
		childSizer = wx.BoxSizer(wx.VERTICAL)
		childLabel = wx.StaticText(
			self,
			wx.ID_ANY,
			# Translators: The label of a list of items to select the type of element
			# in the browse mode Elements List dialog.
			label=NVDAString("&Type:"),
			style=wx.ALIGN_CENTRE)
		childSizer.Add(childLabel, )
		self.childListBox = wx.ListBox(
			self,
			wx.ID_ANY,
			name="TypeName",
			choices=tuple(et[1] for et in self.ELEMENT_TYPES),
			style=wx.LB_SINGLE,
			size=(596, 130))
		if self.childListBox.GetCount():
			self.childListBox.SetSelection(self.lastSelectedElementType)

		self.childListBox.Bind(wx.EVT_LISTBOX, self.onElementTypeChange)
		self.childListBox.Bind(wx.EVT_SET_FOCUS, self.onChildBoxFocus)
		childSizer.Add(self.childListBox)
		contentsSizer.Add(childSizer, flag=wx.EXPAND)
		contentsSizer.AddSpacer(gui.guiHelper.SPACE_BETWEEN_VERTICAL_DIALOG_ITEMS)

		self.tree = wx.TreeCtrl(
			self,
			size=wx.Size(500, 600),
			style=wx.TR_HAS_BUTTONS | wx.TR_HIDE_ROOT | wx.TR_LINES_AT_ROOT | wx.TR_SINGLE | wx.TR_EDIT_LABELS)
		self.tree.Bind(wx.EVT_SET_FOCUS, self.onTreeSetFocus)
		self.tree.Bind(wx.EVT_CHAR, self.onTreeChar)
		self.tree.Bind(wx.EVT_TREE_BEGIN_LABEL_EDIT, self.onTreeLabelEditBegin)
		self.tree.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.onTreeLabelEditEnd)
		self.treeRoot = self.tree.AddRoot("root")
		contentsSizer.Add(self.tree, flag=wx.EXPAND)
		contentsSizer.AddSpacer(gui.guiHelper.SPACE_BETWEEN_VERTICAL_DIALOG_ITEMS)

		# Translators: The label of an editable text field to filter the elements
		# in the browse mode Elements List dialog.
		filterText = NVDAString("Filter b&y:")
		labeledCtrl = gui.guiHelper.LabeledControlHelper(
			self, filterText, wx.TextCtrl)
		self.filterEdit = labeledCtrl.control
		self.filterEdit.Bind(wx.EVT_TEXT, self.onFilterEditTextChange)
		contentsSizer.Add(labeledCtrl.sizer)
		contentsSizer.AddSpacer(gui.guiHelper.SPACE_BETWEEN_VERTICAL_DIALOG_ITEMS)
		bHelper = gui.guiHelper.ButtonHelper(wx.HORIZONTAL)
		# Translators: The label of a button to activate an element
		# in the browse mode Elements List dialog.
		self.activateButton = bHelper.addButton(self, label=NVDAString("Activate"))
		self.activateButton.Bind(wx.EVT_BUTTON, lambda evt: self.onAction(True))
		# Translators: The label of a button to move to an element
		# in the browse mode Elements List dialog.
		self.moveButton = bHelper.addButton(self, label=NVDAString("&Move to"))
		self.moveButton.Bind(wx.EVT_BUTTON, lambda evt: self.onAction(False))
		bHelper.addButton(self, id=wx.ID_CANCEL)

		contentsSizer.Add(bHelper.sizer, flag=wx.ALIGN_RIGHT)
		mainSizer.Add(
			contentsSizer, border=gui.guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)

		self.tree.SetFocus()
		# delay initList to ear the title of window
		wx.CallLater(
			200,
			self.initElementType,
			self.ELEMENT_TYPES[self.lastSelectedElementType][0])
		self.CentreOnScreen()
		self.refreshDialogTitle()

	def refreshDialogTitle(self):
		if self.childListBox.GetCount():
			type = self.childListBox.GetStringSelection()
			title = "%s - %s" % (self.dialogTitle, type)
			self.SetTitle(title)

	def onElementTypeChange(self, evt):
		if self._timer:
			self._timer.Stop()
		elementType = evt.GetInt()
		# We need to make sure this gets executed after the focus event.
		# Otherwise, NVDA doesn't seem to get the event.
		wx.CallLater(200, self.initElementType, self.ELEMENT_TYPES[elementType][0])
		self.lastSelectedElementType = elementType
		self.refreshDialogTitle()

	def initElementType(self, elType):
		if elType in ("link", "button", "radioButton", "checkBox"):
			# Links, buttons, radio button, check box can be activated.
			self.activateButton.Enable()
			self.SetAffirmativeId(self.activateButton.GetId())
		else:
			# No other element type can be activated.
			self.activateButton.Disable()
			self.SetAffirmativeId(self.moveButton.GetId())

		# Gather the elements of this type.
		th = runInThread.RepeatBeep(delay=1.5, beep=(200, 200))
		th.start()
		self._elements = []
		self._initialElement = None

		parentElements = []
		isAfterSelection = False
		maxItemNumber = -1
		try:
			for item in self.document._iterNodesByType(elType):
				if maxItemNumber == 0:
					break
				maxItemNumber = maxItemNumber - 1 if maxItemNumber >= 0 else maxItemNumber
				# Find the parent element, if any.
				for parent in reversed(parentElements):
					if item.isChild(parent.item):
						break
					else:
						# We're not a child of this parent,
						# so this parent has no more children and can be removed from the stack.
						parentElements.pop()
				else:
					# No parent found, so we're at the root.
					# Note that parentElements will be empty at this point,
					# as all parents are no longer relevant
					# and have thus been removed from the stack.
					parent = None
				element = self.Element(item, parent)
				self._elements.append(element)
				if not isAfterSelection:
					isAfterSelection = item.isAfterSelection
					if not isAfterSelection:
						# The element immediately preceding or overlapping the caret should be
						# the initially selected element.
						# Since we have not yet passed the selection,
						# use this as the initial element.
						try:
							self._initialElement = self._elements[-1]
						except IndexError:
							# No previous element.
							pass
				# This could be the parent of a subsequent element,
				# so add it to the parents stack.
				parentElements.append(element)
		except Exception:
			pass
		# Start with no filtering.
		self.filterEdit.ChangeValue("")
		self.filter("", newElementType=True)
		self.sayNumberOfElements()
		th.stop()

	def Destroy(self):
		if self._timer is not None:
			self._timer .Stop()
			self._timer = None
		super(ElementsListDialogEx, self).Destroy()

	def sayNumberOfElements(self):
		def callback(count):
			self._timer = None
			if not self.childListBox.HasFocus():
				return
			if count:
				# Translators: message to the user to report number of elements.
				msg = _("%s elements") % str(count) if count > 1 else _("One element")
				queueHandler.queueFunction(
					queueHandler.eventQueue, ui.message, msg)
			else:
				# Translators: message to the user when there is no element.
				queueHandler.queueFunction(
					queueHandler.eventQueue, ui.message, _("no element"))
		if self._timer:
			self._timer.Stop()
		self._timer = wx.CallLater(600, callback, self.tree.Count)

	def onChildBoxFocus(self, evt):
		self.sayNumberOfElements()

	def filter(self, filterText, newElementType=False):
		# If this is a new element type, use the element nearest the cursor.
		# Otherwise, use the currently selected element.
		# #8753: wxPython 4 returns "invalid tree item"
		# when the tree view is empty, so use initial element if appropriate.
		try:
			defaultElement = self._initialElement if newElementType else self.tree.GetItemData(
				self.tree.GetSelection())
		except Exception:
			defaultElement = self._initialElement
		# Clear the tree.
		self.tree.DeleteChildren(self.treeRoot)

		# Populate the tree with elements matching the filter text.
		elementsToTreeItems = {}
		defaultItem = None
		matched = False
		# Do case-insensitive matching by lowering both filterText
		# and each element's text.
		filterText = filterText.lower()
		for element in self._elements:
			try:
				label = element.item.label
			except Exception:
				label = ""
			if filterText and filterText not in label.lower():
				continue
			matched = True
			parent = element.parent
			if parent:
				parent = elementsToTreeItems.get(parent)
			item = self.tree.AppendItem(parent or self.treeRoot, label)
			self.tree.SetItemData(item, element)
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
		# If the activate button isn't the default button,
		# it is disabled for this element type and shouldn't be enabled here.
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
			# The enter key should be propagated to the dialog
			# and thus activate the default button,
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
			item = self.tree.GetSelection()
			if item:
				# selectedItemType = self.tree.GetItemData(item).item
				self.tree.EditLabel(item)
				evt.Skip()

		elif key >= wx.WXK_START or key == wx.WXK_BACK:
			# Non-printable character.
			self._searchText = ""
			evt.Skip()

		else:
			# Search the list.
			# We have to implement this ourselves,
			# as tree views don't accept space as a search character.
			char = chr(evt.UnicodeKey).lower()
			# IF the same character is typed twice, do the same search.
			if self._searchText != char:
				self._searchText += char
			if self._searchCallLater:
				self._searchCallLater.Restart()
			else:
				self._searchCallLater = wx.CallLater(1000, self._clearSearchText)
			self.search(self._searchText)

	def onTreeLabelEditBegin(self, evt):
		item = self.tree.GetSelection()
		selectedItemType = self.tree.GetItemData(item).item
		if not selectedItemType.isRenameAllowed:
			evt.Veto()

	def onTreeLabelEditEnd(self, evt):
		selectedItemNewName = evt.GetLabel()
		item = self.tree.GetSelection()
		selectedItemType = self.tree.GetItemData(item).item
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
		items = itertools.chain(
			self._iterReachableTreeItemsFromItem(item),
			self._iterReachableTreeItemsFromItem(
				self.tree.GetFirstChild(self.treeRoot)[0]))
		if len(searchText) == 1:
			# If only a single character has been entered,
			# skip (search after) the current item.
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
		# Save off the last selected element type on to the class
		# so its used in initialization next time.
		self.__class__.lastSelectedElementType = self.lastSelectedElementType
		item = self.tree.GetSelection()
		item = self.tree.GetItemData(item).item
		if activate:
			item.activate()
		else:

			def move():
				speech.cancelSpeech()
				# #8831: Report before moving because moving might change the focus, which
				# might mutate the document, potentially invalidating info if it is
				# offset-based.
				item.report()
				item.moveTo()
			# We must use core.callLater rather than wx.CallLater to ensure
				# that the callback runs within NVDA's core pump.
			# If it didn't, and it directly or indirectly called wx.Yield,
				# it could start executing NVDA's core pump from within the yield,
				# causing recursion.
			core.callLater(100, move)


class GeckoElementsListDialog(ElementsListDialogEx):
	ELEMENT_TYPES = (
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("link", NVDAString("link").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("heading", NVDAString("heading").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("formField", _("Form field")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("button", NVDAString("button").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("landmark", NVDAString("landmark").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("radioButton", NVDAString("radio button").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("paragraph", NVDAString("paragraph").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("frame", NVDAString("frame").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("division", NVDAString("division").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("checkBox", NVDAString("check box").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("comboBox", NVDAString("combo box").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("table", NVDAString("table").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("blocQuote", NVDAString("block quote").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("edit", NVDAString("edit").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("list", NVDAString("list").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("listItem", NVDAString("list item").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("anchor", _("Anchor")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("graphic", NVDAString("graphic").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("embeddedObject", NVDAString("embedded object").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("separator", NVDAString("separator").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("clickable", NVDAString("clickable").capitalize()),
	)
	Element = collections.namedtuple("Element", ("item", "parent"))
	lastSelectedElementType = 0
	_timer = None
