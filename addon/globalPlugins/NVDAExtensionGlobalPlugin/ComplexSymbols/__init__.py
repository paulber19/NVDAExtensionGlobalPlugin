# globalPlugins\NVDAExtensionGlobalPlugin\ComplexSymbols\__init__.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2018 - 2021 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import addonHandler
from logHandler import log
import time
import wx
from keyboardHandler import KeyboardInputGesture
import ui
import speech
import gui
from gui import guiHelper
import core
import config
from . import symbols
from api import copyToClip
from ..utils.NVDAStrings import NVDAString
from ..utils import speakLater, isOpened, makeAddonWindowTitle, getHelpObj
from ..utils import contextHelpEx

addonHandler.initTranslation()


_lastUsedSymbols = []


def SendKey(keys):
	KeyboardInputGesture.fromName(keys).send()


class complexSymbolsDialog(
	contextHelpEx.ContextHelpMixinEx,
	wx.Dialog):
	shouldSuspendConfigProfileTriggers = True
	_instance = None
	title = None
	# help in the user manual.
	helpObj = getHelpObj("hdr3-1")

	def __new__(cls, *args, **kwargs):
		if complexSymbolsDialog._instance is not None:
			return complexSymbolsDialog._instance
		return wx.Dialog.__new__(cls)

	def __init__(self, parent, symbolsManager):
		if complexSymbolsDialog._instance is not None:
			return
		complexSymbolsDialog._instance = self
		# Translators: This is the title of complex symbols dialog window.
		dialogTitle = _("Help for complex symbols edition")
		title = complexSymbolsDialog.title = makeAddonWindowTitle(dialogTitle)
		super(complexSymbolsDialog, self).__init__(
			parent, -1, title, style=wx.CAPTION | wx.CLOSE_BOX | wx.TAB_TRAVERSAL)
		self.symbolsManager = symbolsManager
		self.basicCategoryNamesList = self.symbolsManager.getBasicCategoryNames()
		self.categoryNamesList = self.symbolsManager.getCategoryNames()
		self.curIndexInSymbolCategoryListBox = 0
		self.InitLists()
		self.doGui()

	def InitLists(self, index=0):
		categoryName = self.categoryNamesList[index]
		(symbolList, descriptionList) = self.symbolsManager.getSymbolAndDescriptionList(categoryName)
		self.complexSymbolsList = symbolList[:]
		self.symbolDescriptionList = descriptionList[:]

	def doGui(self):
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# the category list box
		# Translators: This is a label appearing on complex symbols dialog.
		symbolCategoryListLabelText = _("&Categories:")
		self.symbolCategoryListBox_ID = wx.NewIdRef()
		self.symbolCategoryListBox = sHelper.addLabeledControl(
			symbolCategoryListLabelText,
			wx.ListBox,
			id=self.symbolCategoryListBox_ID,
			name="CategoryNames",
			choices=self.categoryNamesList,
			style=wx.LB_SINGLE | wx.LB_ALWAYS_SB | wx.WANTS_CHARS,
			size=(948, 130))
		if self.symbolCategoryListBox.GetCount():
			self.symbolCategoryListBox.SetSelection(0)
		# the symbol list box
		# Translators: This is a label appearing on complex symbols dialog.
		symbolsListLabelText = _("S&ymbols:")
		self.symbolsListBox = sHelper.addLabeledControl(
			symbolsListLabelText,
			wx.ListBox,
			id=wx.ID_ANY,
			name="symbols list",
			choices=self.symbolDescriptionList,
			style=wx.LB_SINGLE | wx.LB_ALWAYS_SB,
			size=(948, 390))
		# Buttons
		# Buttons are in a horizontal row
		bHelper = guiHelper.ButtonHelper(wx.HORIZONTAL)
		copyButton = bHelper.addButton(
			self,
			# Translators: This is a label of a button appearing
			# on complex symbols dialog.
			label=_("&Copy to clipboard"))
		pasteButton = bHelper.addButton(
			self,
			# Translators: This is a label of a button appearing
			# on complex symbols dialog.
			label=_("&Paste"))
		pasteButton.SetDefault()
		manageSymbolsButton = bHelper.addButton(
			self,
			# Translators: This is a label of a button appearing
			# on complex symbols dialog.
			label=_("&Manage your symbols"))
		sHelper.addItem(bHelper)
		bHelper = sHelper.addDialogDismissButtons(
			gui.guiHelper.ButtonHelper(wx.HORIZONTAL))
		closeButton = bHelper.addButton(
			self, id=wx.ID_CLOSE, label=NVDAString("&Close"))
		mainSizer.Add(
			sHelper.sizer, border=guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		# Events
		copyButton.Bind(wx.EVT_BUTTON, self.onCopyButton)
		pasteButton.Bind(wx.EVT_BUTTON, self.onPasteButton)
		manageSymbolsButton.Bind(wx.EVT_BUTTON, self.onManageSymbolsButton)
		closeButton.Bind(wx.EVT_BUTTON, lambda evt: self.Destroy())
		self.symbolCategoryListBox.Bind(wx.EVT_LISTBOX, self.onSelectCategory)
		self.symbolCategoryListBox.Bind(wx.EVT_KEY_DOWN, self.onKeydown)
		self.symbolsListBox.Bind(wx.EVT_KEY_DOWN, self.onKeydown)
		self.SetEscapeId(wx.ID_CLOSE)

	def Destroy(self):
		complexSymbolsDialog._instance = None
		super(complexSymbolsDialog, self).Destroy()

	def onSelectCategory(self, event):
		index = self.symbolCategoryListBox.GetSelection()
		self.curIndexInSymbolCategoryListBox = index
		if index >= 0:
			self.InitLists(index)
			# update symbolListBox
			self.symbolsListBox.Clear()
			self.symbolsListBox.AppendItems(self.symbolDescriptionList)

		event.Skip()

	def onKeydown(self, event):
		keyCode = event.GetKeyCode()
		if keyCode == wx.WXK_SPACE:
			index = self.symbolsListBox.GetSelection()
			if index == -1:
				return
			symbol = self.complexSymbolsList[index]
			c = ord(symbol)
			core.callLater(400, ui.message, "%d," % c)
			core.callLater(450, speech.speakSpelling, hex(c))
			return
		if keyCode == wx.WXK_TAB:
			shiftDown = event.ShiftDown()
			if shiftDown:
				wx.Window.Navigate(
					self.symbolCategoryListBox, wx.NavigationKeyEvent.IsBackward)
			else:
				wx.Window.Navigate(
					self.symbolCategoryListBox, wx.NavigationKeyEvent.IsForward)
			return
		id = event.GetId()
		if keyCode == wx.WXK_RETURN and id == self.symbolCategoryListBox_ID:
			wx.Window.Navigate(
				self.symbolCategoryListBox, wx.NavigationKeyEvent.IsForward)
			return
		event.Skip()

	def onPasteButton(self, event):
		index = self.symbolsListBox.GetSelection()
		if index == -1:
			# Translators: This is a message announced in complex symbols dialog.
			speakLater(300, _("No symbol selected"))
			return
		symbol = self.complexSymbolsList[index]
		symbolDescription = self.symbolsListBox.GetString(index)
		result = copyToClip(symbol)
		if not result:
			c = ord(symbol)
			log.error("error copyToClip symbol:%s (%s) code = %d" % (
				self.symbolDescriptionList[index], symbol, c))
		else:
			# Translators: This is a message announced in complex symbols dialog.
			msg = _("{0} pasted").format(self.symbolDescriptionList[index])
			ui.message(msg)
			time.sleep(2.0)
			core.callLater(200, SendKey, "Control+v")
		from ..settings.nvdaConfig import _NVDAConfigManager
		_NVDAConfigManager.updateLastSymbolsList(symbolDescription, symbol)
		self.Close()

	def onCopyButton(self, event):
		index = self.symbolsListBox.GetSelection()
		if index == -1:
			# Translators: This is a message announced in complex symbols dialog.
			speakLater(300, _("No symbol selected"))
			return
		symbol = self.complexSymbolsList[index]
		symbolDescription = self.symbolsListBox.GetString(index)
		result = copyToClip(symbol)
		if not result:
			c = ord(symbol)
			log.warning("error copyToClip symbol:%s (%s) code = %d" % (self.symbolDescriptionList[index], symbol, c))
			# Translators: message to the user to report copy to clipboard error.
			msg = _("Symbol cannot copied to the clipboard")
		else:
			# Translators: This is a message announced in complex symbols dialog.
			msg = _("{0} copied").format(self.symbolDescriptionList[index])
		ui.message(msg)
		time.sleep(2.0)
		from ..settings.nvdaConfig import _NVDAConfigManager
		_NVDAConfigManager .updateLastSymbolsList(symbolDescription, symbol)
		self.Close()

	def onManageSymbolsButton(self, evt):
		with ManageSymbolsDialog(self) as d:
			d.ShowModal()

			if d.noChange:
				return
			categoryName = self.symbolCategoryListBox.GetStringSelection()
			self.categoryNamesList = self.symbolsManager.getCategoryNames()
			self.symbolCategoryListBox.Clear()
			self.symbolCategoryListBox.AppendItems(self.categoryNamesList)
			index = 0
			if categoryName in self.categoryNamesList:
				index = self.categoryNamesList .index(categoryName)
			self.symbolCategoryListBox.SetSelection(index)
			self.onSelectCategory(evt)
			self.symbolCategoryListBox.SetFocus()

	@classmethod
	def run(cls):
		if isOpened(cls):
			return
		symbolsManager = symbols.SymbolsManager()
		if not symbolsManager.isReady():
			gui.messageBox(
				# Translators: the label of a message box dialog.
				_("Error: no basic symbols installed"),
				# Translators: the title of a message box dialog.
				_("Warning"),
				wx.OK | wx.ICON_WARNING)
			return
		gui.mainFrame.prePopup()
		d = cls(gui.mainFrame, symbolsManager)
		d.CentreOnScreen()
		d.Show()
		gui.mainFrame.postPopup()


class ManageSymbolsDialog(
	contextHelpEx.ContextHelpMixinEx,
	wx.Dialog):
	shouldSuspendConfigProfileTriggers = True
	# Translators: This is the title of Manage Symbols Dialog window.
	title = _("User symbols manager")
	# help in the user manual.
	helpObj = getHelpObj("hdr3-1")

	def __init__(self, parent):
		super(ManageSymbolsDialog, self).__init__(
			None, -1, title=self.title,
			style=wx.CAPTION | wx.CLOSE_BOX | wx.TAB_TRAVERSAL)
		self.noChange = True
		self.parent = parent
		self.symbolsManager = self.parent.symbolsManager
		self.userComplexSymbols = self.symbolsManager.getUserSymbolCategories()
		self.curCategoryIndex = parent.curIndexInSymbolCategoryListBox
		self.categoryNamesList = parent.categoryNamesList
		self.InitLists(self.parent.symbolCategoryListBox.GetSelection())
		self.doGui()
		self.CentreOnScreen()

	def InitLists(self, index=0):
		categoryName = self.categoryNamesList[index]
		(symbolList, descriptionList) = self.symbolsManager.getUserSymbolAndDescriptionList(
			categoryName, self.userComplexSymbols)
		self.symbolDescriptionList = descriptionList[:]
		self.complexSymbolsList = symbolList[:]

	def doGui(self):
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# the category list box
		# Translators: This is a label appearing on Manage Symbols Dialog.
		symbolCategoryListLabelText = _("&Categories:")
		self.symbolCategoryListBox_ID = wx.NewIdRef()
		self.symbolCategoryListBox = sHelper.addLabeledControl(
			symbolCategoryListLabelText,
			wx.ListBox,
			id=self.symbolCategoryListBox_ID,
			name="Categories",
			choices=self.categoryNamesList,
			style=wx.LB_SINGLE | wx.LB_ALWAYS_SB | wx.WANTS_CHARS,
			size=(948, 130))
		if self.symbolCategoryListBox.GetCount():
			self.symbolCategoryListBox.SetSelection(self.curCategoryIndex)
		# the symbol list box
		# Translators: This is a label appearing on Manage Symbols Dialog.
		symbolsListLabelText = _("S&ymbols:")
		self.symbolsListBox = sHelper.addLabeledControl(
			symbolsListLabelText,
			wx.ListBox,
			id=wx.ID_ANY,
			name="symbols list",
			choices=self.symbolDescriptionList,
			style=wx.LB_SINGLE,
			size=(948, 390))

		# first line of Buttons
		bHelper = guiHelper.ButtonHelper(wx.HORIZONTAL)
		# Translators: This is a label of a button appearing
		# on Manage Symbols Dialog.
		addSymbolButton = bHelper.addButton(self, label=_("&Add a symbol"))
		# Translators: This is a label of a button appearing
		# on Manage Symbols Dialog.
		deleteSymbolButton = bHelper.addButton(self, label=_("&Delete the symbol"))
		# Translators: This is a label of a button appearing
		# on Manage Symbols Dialog.
		addCategoryButton = bHelper.addButton(self, label=_("Add a &category"))
		# Translators: This is a label of a button appearing
		# on Manage Symbols Dialog.
		self.deleteCategoryButton = bHelper.addButton(
			self, label=_("De&lete the category"))
		sHelper.addItem(bHelper)
		# second line of buttons
		bHelper = sHelper.addDialogDismissButtons(
			gui.guiHelper.ButtonHelper(wx.HORIZONTAL))
		# Translators: This is a label of a button appearing
		# on Manage Symbols Dialog.
		saveButton = bHelper.addButton(self, label=_("&Save"))
		bHelper.addButton(self, id=wx.ID_CANCEL)
		mainSizer.Add(
			sHelper.sizer, border=guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		# Events
		addSymbolButton.Bind(wx.EVT_BUTTON, self.onAddSymbolButton)
		deleteSymbolButton.Bind(wx.EVT_BUTTON, self.onDeleteSymbolButton)
		addCategoryButton.Bind(wx.EVT_BUTTON, self.onAddCategoryButton)
		self.deleteCategoryButton.Bind(wx.EVT_BUTTON, self.onDeleteCategoryButton)
		saveButton.Bind(wx.EVT_BUTTON, self.onSaveButton)
		self.symbolCategoryListBox.Bind(wx.EVT_LISTBOX, self.onSelect)
		self.symbolCategoryListBox.Bind(wx.EVT_KEY_DOWN, self.onKeydown)
		self.symbolsListBox.Bind(wx.EVT_KEY_DOWN, self.onKeydown)
		self.SetEscapeId(wx.ID_CANCEL)
		self.updateButtons()

	def updateButtons(self):
		categoryName = self.symbolCategoryListBox.GetStringSelection()
		if categoryName in self.parent.basicCategoryNamesList:
			self.deleteCategoryButton.Disable()
		else:
			self.deleteCategoryButton.Enable()

	def onSelect(self, event):
		index = self.symbolCategoryListBox.GetSelection()
		if index >= 0:
			self.InitLists(index)
			# update symbolListBox
			self.symbolsListBox.Clear()
			self.symbolsListBox.AppendItems(self.symbolDescriptionList)
		self.updateButtons()
		event.Skip()

	def onKeydown(self, evt):
		keyCode = evt.GetKeyCode()
		if keyCode == wx.WXK_SPACE:
			index = self.symbolsListBox.GetSelection()

			if index == -1:
				return
			symbol = self.complexSymbolsList[index]
			c = ord(symbol)
			core.callLater(400, speech.speakMessage, "%d," % c)
			core.callLater(450, speech.speakSpelling, hex(c))
			return

		if keyCode == wx.WXK_TAB:
			shiftDown = evt.ShiftDown()
			if shiftDown:
				wx.Window.Navigate(
					self.symbolCategoryListBox, wx.NavigationKeyEvent.IsBackward)
			else:
				wx.Window.Navigate(
					self.symbolCategoryListBox, wx.NavigationKeyEvent.IsForward)
			return
		id = evt.GetId()
		if keyCode == wx.WXK_RETURN and id == self.symbolCategoryListBox_ID:
			wx.Window.Navigate(
				self.symbolCategoryListBox, wx.NavigationKeyEvent.IsForward)
			return
		evt.Skip()

	def onDeleteSymbolButton(self, evt):
		index = self.symbolsListBox.GetSelection()
		if index == -1:
			core.callLater(
				300,
				ui.message,
				# Translators: This is a message announced in Manage Symbols Dialog.
				_("No symbol selected"))
			return

		symbol = self.complexSymbolsList[index]
		description = self.symbolsListBox.GetStringSelection()
		categoryName = self.symbolCategoryListBox.GetStringSelection()
		del self.userComplexSymbols[categoryName][symbol]
		self.onSelect(evt)
		core.callLater(
			300,
			ui.message,
			# Translators: This is a message announced in Manage Symbols Dialog.
			_("%s symbol deleted") % description)
		evt.Skip()

	def validateSymbol(self, categoryName, symbol, description):
		if len(symbol) == 0 and len(description) == 0:
			return False
		if len(symbol) == 0:
			# Translators: This is a message announced in Manage Symbols Dialog.
			core.callLater(300, ui.message, _("No symbol entered"))
			return False
		if len(symbol) > 1:
			core.callLater(
				300,
				ui.message,
				# Translators: This is a message announced in Manage Symbols Dialog.
				_("Symbol is not valid"))
			return False
		if len(description) == 0:
			core.callLater(
				300,
				ui.message,
				# Translators: This is a message announced in Manage Symbols Dialog.
				_("There is no description for the symbol"))
			return False
		for cat in self.parent.categoryNamesList:
			(symbolList, descriptionList) = self.symbolsManager.getSymbolAndDescriptionList(cat)
			if symbol in symbolList:
				description = descriptionList[symbolList.index(symbol)]
				if cat == categoryName:
					if gui.messageBox(
						# Translators: the label of a message box dialog.
						_(
							"""The symbol is already in this category """
							"""under "%s" description. Do you want to replace it?""") % description,
						# Translators: the title of a message box dialog.
						_("Confirmation"),
						wx.YES | wx.NO | wx.ICON_WARNING) == wx.NO:
						return False
				else:
					if gui.messageBox(
						# Translators: the label of a message box dialog.
						_(
							"""The symbol is allready in "{oldCat}" category. """
							"""Do you want to add this symbol also in "{newCat}" category?""").format(
								oldCat=cat, newCat=categoryName),
						# Translators: the title of a message box dialog.
						_("Confirmation"),
						wx.YES | wx.NO | wx.ICON_WARNING) == wx.NO:
						return False
		return True

	def onAddSymbolButton(self, evt):
		categoryName = self.symbolCategoryListBox.GetStringSelection()
		with AddSymbolDialog(self, categoryName) as entryDialog:
			if entryDialog.ShowModal() != wx.ID_OK:
				return
			symbol = entryDialog.symbolEdit.GetValue()
			description = entryDialog.descriptionEdit.GetValue()
			if not self.validateSymbol(categoryName, symbol, description):
				return
			if categoryName not in self.userComplexSymbols:
				self.userComplexSymbols[categoryName] = {}
			self.userComplexSymbols[categoryName][symbol] = description
			self.onSelect(evt)
			core.callLater(
				300,
				ui.message,
				# Translators: This is a message announced in Manage Symbols Dialog.
				_("%s symbol has been added") % description)
		evt.Skip()

	def onAddCategoryButton(self, evt):
		with wx.TextEntryDialog(
			self,
			# Translators: Message to show on the dialog.
			_("Enter category name:"),
			# Translators: This is a title of text control of dialog box
			# in Manage Symbols Dialog.
			_("Adding category"),
			"") as entryDialog:
			if entryDialog.ShowModal() != wx.ID_OK:
				return
			categoryName = entryDialog.Value
			if categoryName in self.userComplexSymbols\
				or categoryName in self.categoryNamesList:
				core.callLater(
					300,
					ui.message,
					# Translators: message announced in Manage Symbols Dialog.
					_(""""%s" category already exists""") % categoryName)
			else:
				self.userComplexSymbols[categoryName] = {}
				self.categoryNamesList.append(categoryName)
				self.symbolCategoryListBox.Clear()
				self.symbolCategoryListBox.AppendItems(self.categoryNamesList)
				self.symbolCategoryListBox.SetSelection(
					self.categoryNamesList.index(categoryName))
				self.onSelect(evt)
		evt.Skip()

	def onDeleteCategoryButton(self, evt):
		categoryName = self.symbolCategoryListBox.GetStringSelection()
		if categoryName in self.parent.basicCategoryNamesList:
			core.callLater(
				300,
				ui.message,
				# Translators: This is a message announced in Manage Symbols Dialog.
				_("You cannot delete this basic category."))
			return
		index = self.categoryNamesList.index(categoryName)
		if gui.messageBox(
			# Translators: the label of a message box dialog.
			_("Do you really want to delete this category and all its symbols?"),
			# Translators: the title of a message box dialog.
			_("Confirmation"),
			wx.YES | wx.NO | wx.ICON_WARNING) == wx.NO:
			return

		if index == len(self.categoryNamesList) - 1:
			index = index - 1 if index else index
		del self.userComplexSymbols[categoryName]
		self.categoryNamesList.remove(categoryName)
		self.symbolCategoryListBox.Clear()
		self.symbolCategoryListBox.AppendItems(self.categoryNamesList)
		self.symbolCategoryListBox.SetSelection(index)
		core.callLater(
			300,
			ui.message,
			# Translators: This is a message announced in Manage Symbols Dialog.
			_(""""%s" category has been deleted""") % categoryName)
		self.onSelect(evt)
		evt.Skip()

	def onSaveButton(self, evt):
		self.symbolsManager.saveUserSymbolCategories(self.userComplexSymbols)
		self.noChange = False
		self.Close()


class AddSymbolDialog(
	contextHelpEx.ContextHelpMixinEx,
	wx.Dialog):
	shouldSuspendConfigProfileTriggers = True
	# Translators: This is the title of the add symbol dialog.
	title = _("Adding Symbol in %s category")
	# help id in the user manual.
	helpObj = getHelpObj("hdr3-1")

	def __init__(self, parent, categoryName):
		super(AddSymbolDialog, self).__init__(
			parent, title=self.title % categoryName)
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = gui.guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# Translators: This is the label of the edit field appearing
		# on the add symbol dialog.
		symbolEditLabelText = _("Enter the Symbol:")
		self.symbolEdit = sHelper.addLabeledControl(symbolEditLabelText, wx.TextCtrl)
		# Translators: This is the label of symbol description edit field appearing
		# on in the add symbol dialog.
		descriptionEditLabelText = _("Enter the Description:")
		self.descriptionEdit = sHelper.addLabeledControl(
			descriptionEditLabelText, wx.TextCtrl)
		sHelper.addDialogDismissButtons(self.CreateButtonSizer(wx.OK | wx.CANCEL))
		mainSizer.Add(
			sHelper.sizer, border=gui.guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		self.symbolEdit.SetFocus()
		self.CentreOnScreen()


class LastUsedComplexSymbolsDialog(
	contextHelpEx.ContextHelpMixinEx,
	wx.Dialog):
	shouldSuspendConfigProfileTriggers = True
	_instance = None
	title = None
	# help id in the user manual.
	helpObj = getHelpObj("hdr3-2")

	def __new__(cls, *args, **kwargs):
		if LastUsedComplexSymbolsDialog._instance is not None:
			return LastUsedComplexSymbolsDialog._instance
		return wx.Dialog.__new__(cls)

	def __init__(self, parent, lastUsedSymbols):
		if LastUsedComplexSymbolsDialog._instance is not None:
			return
		LastUsedComplexSymbolsDialog._instance = self
		profileName = config.conf.profiles[-1].name
		if profileName is None:
			profileName = NVDAString("normal configuration")
		# Translators: This is the title of Last Used Complex Symbols Dialog.
		dialogTitle = _("Last used complex symbols")
		dialogTitle = "%s (%s)" % (dialogTitle, profileName)
		LastUsedComplexSymbolsDialog.title = makeAddonWindowTitle(dialogTitle)
		super(LastUsedComplexSymbolsDialog, self).__init__(
			parent,
			-1,
			LastUsedComplexSymbolsDialog.title,
			style=wx.CAPTION | wx.CLOSE_BOX | wx.TAB_TRAVERSAL)
		self.lastUsedSymbols = lastUsedSymbols
		self.doGui()

	def doGui(self):
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# the last used symbols list
		# Translators: a label appearing on Last used complex symbols dialog.
		symbolsListLabelText = _("&Symbols:")
		self.symbolsListBox_ID = wx.NewIdRef()
		self.symbolsListBox = sHelper.addLabeledControl(
			symbolsListLabelText,
			wx.ListBox,
			id=self.symbolsListBox_ID,
			name="Symbols",
			choices=[desc for (desc, symbol) in self.lastUsedSymbols],
			style=wx.LB_SINGLE | wx.LB_ALWAYS_SB,
			size=(948, 130))
		if self.symbolsListBox.GetCount():
			self.symbolsListBox.SetSelection(0)
		# Buttons
		# Buttons are in a horizontal row
		bHelper = guiHelper.ButtonHelper(wx.HORIZONTAL)
		# Translators: This is a label of a button appearing
		# on Last Used Complex Symbols Dialog.
		copyButton = bHelper.addButton(self, label=_("&Copy to clipboard"))
		# Translators: This is a label of a button appearing
		# on Last Used Complex Symbols Dialog.
		pasteButton = bHelper.addButton(self, label=_("&Past"))
		pasteButton.SetDefault()
		# Translators: This is a label of a button appearing
		# on last Used Symbols dialog.
		cleanButton = bHelper.addButton(self, label=_("&Delete all"))
		sHelper.addItem(bHelper)
		bHelper = sHelper.addDialogDismissButtons(
			gui.guiHelper.ButtonHelper(wx.HORIZONTAL))
		closeButton = bHelper.addButton(
			self, id=wx.ID_CLOSE, label=NVDAString("&Close"))
		mainSizer.Add(
			sHelper.sizer, border=guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
		mainSizer.Fit(self)
		self.SetSizer(mainSizer)
		# Events
		copyButton.Bind(wx.EVT_BUTTON, self.onCopyButton)
		pasteButton.Bind(wx.EVT_BUTTON, self.onPasteButton)
		cleanButton.Bind(wx.EVT_BUTTON, self.onCleanButton)
		closeButton.Bind(wx.EVT_BUTTON, lambda evt: self.Destroy())
		self.SetEscapeId(wx.ID_CLOSE)

	def Destroy(self):
		LastUsedComplexSymbolsDialog._instance = None
		super(LastUsedComplexSymbolsDialog, self).Destroy()

	def onPasteButton(self, event):
		index = self.symbolsListBox.GetSelection()
		if index == -1:
			# Translators: a message announced in Last Used Complex Symbols Dialog.
			speakLater(300, _("No symbol selected"))
			return
		(description, symbol) = self.lastUsedSymbols[index]
		result = copyToClip(symbol)
		if not result:
			c = ord(symbol)
			log.error(
				"error copyToClip symbol:%s (%s) code = %d" % (description, symbol, c))
		else:
			# Translators: This is a message announced in complex symbols dialog.
			msg = _("{0} pasted").format(description)
			ui.message(msg)
			time.sleep(2.0)
			core.callLater(200, SendKey, "Control+v")
		self.Close()

	def onCopyButton(self, event):
		index = self.symbolsListBox.GetSelection()
		if index == -1:
			# Translators: a message announced in Last Used Complex Symbols Dialog.
			speakLater(300, _("No symbol selected"))
			return
		(description, symbol) = self.lastUsedSymbols[index]
		result = copyToClip(symbol)
		if not result:
			c = ord(symbol)
			log.error("error copyToClip symbol:%s (%s) code = %d" % (description, symbol, c))
		else:
			# Translators: a message announced in Last Used Complex Symbols Dialog.
			text = _("{0} copied").format(description)
			ui.message(text)
			time.sleep(2.0)
		self.Close()

	def onCleanButton(self, event):
		if gui.messageBox(
			# Translators: the label of a message box dialog.
			_("Do you really want to delete all symbols of the list?"),
			# Translators: the title of a message box dialog.
			_("Confirmation"),
			wx.YES | wx.NO) == wx.YES:
			from ..settings.nvdaConfig import _NVDAConfigManager
			_NVDAConfigManager.cleanLastUsedSymbolsList()
		self.Close()

	@classmethod
	def run(cls):
		if isOpened(cls):
			return
		from ..settings.nvdaConfig import _NVDAConfigManager
		lastUsedSymbols = _NVDAConfigManager.getLastUsedSymbols()
		if len(lastUsedSymbols) == 0:
			# Translators: message to the user when there is no used symbol recorded.
			ui.message(_("There is no symbol recorded"))
			return
		gui.mainFrame.prePopup()
		d = cls(gui.mainFrame, lastUsedSymbols)
		d.CentreOnScreen()
		d.Show()
		gui.mainFrame.postPopup()
