# globalPlugins\NVDAExtensionGlobalPlugin\clipboardCommandAnnouncement\addToClip.py
# a part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2021-2023 Paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

# this code comes originaly from clipContentsDesigner add-on
# (authors: Noelia Ruiz Martenez, other contributors)


import addonHandler
import api
import textInfos
try:
	# for NVDA version >= 2021.2
	from controlTypes.role import Role
	ROLE_MATH = Role.MATH
except ImportError:
	from controlTypes import ROLE_MATH
import ui
import browseMode
import core
import wx
import gui
from ..settings.nvdaConfig import _NVDAConfigManager

addonHandler.initTranslation()


def getBookmark() -> str:
	separator = _NVDAConfigManager.getAddToClipSeparator()
	if not separator:
		bookmark = "\r\n"
	else:
		bookmark = "\r\n%s\r\n" % separator
	return bookmark


def getSelectedText():
	obj = api.getFocusObject()
	treeInterceptor = obj.treeInterceptor
	if isinstance(treeInterceptor, browseMode.BrowseModeDocumentTreeInterceptor):
		obj = treeInterceptor
	try:
		info = obj.makeTextInfo(textInfos.POSITION_SELECTION)
	except (RuntimeError, NotImplementedError):
		info = None
	if not info or info.isCollapsed:
		return None
	return info.clipboardText


def getMath():
	import mathPres
	mathMl = mathPres.getMathMlFromTextInfo(api.getReviewPosition())
	if not mathMl:
		obj = api.getNavigatorObject()
		if obj.role == ROLE_MATH:
			try:
				mathMl = obj.mathMl
			except (NotImplementedError, LookupError):
				mathMl = None
	if not mathMl:
		return
	mathPres.ensureInit()
	if mathPres.brailleProvider:
		text = mathPres.brailleProvider.getBrailleForMathMl(mathMl)
		return text


def getTextToAdd():
	newText = getSelectedText() or getMath()
	if not newText:
		if not getattr(
			api.getReviewPosition().obj,
			"_selectThenCopyRange", None
		) or not api.getReviewPosition().obj._selectThenCopyRange:
			# Translators: message presented when it's not possible to add text, since no text has been selected.
			ui.message(_("No text to add"))
			return
		newText = api.getReviewPosition().obj._selectThenCopyRange.clipboardText
	try:
		clipData = api.getClipData()
	except Exception:
		clipData = None
	if clipData:
		if _NVDAConfigManager.toggleAddTextBeforeOption(False):
			text = newText + getBookmark() + clipData
		else:
			text = clipData + getBookmark() + newText
	else:
		text = newText
	return text


def confirmAdd():
	text = getTextToAdd()
	if not text:
		return
	if gui.messageBox(
		# Translators: Label of a dialog.
		_("Do you want realy add the selected text to the clipboard?"),
		# Translators: Title of a dialog.
		_("Adding text to clipboard"),
		wx.YES | wx.NO | wx.CANCEL
	) == wx.YES:
		if api.copyToClip(text):
			# Translators: message presented when the text has been added to the clipboard.
			core.callLater(200, ui.message, _("Added"))
		else:
			# Translators: message presented when the text cannot be added to the clipboard.
			core.callLater(200, ui.message, _("Cannot add"))


def performAdd():
	text = getTextToAdd()
	if text is None or len(text) == 0:
		return
	if api.copyToClip(text):
		# Translators: message presented when the text has been added to the clipboard.
		ui.message(_("Added"))
	else:
		# Translators: message presented when the text cannot be added to the clipboard.
		ui.message(_("Cannot add"))


isInAddToClip = False


def addToClip():
	global isInAddToClip
	if isInAddToClip:
		return
	isInAddToClip = True
	if _NVDAConfigManager.toggleConfirmToAddToClipOption(False):
		confirmAdd()
	else:
		performAdd()
	isInAddToClip = False
