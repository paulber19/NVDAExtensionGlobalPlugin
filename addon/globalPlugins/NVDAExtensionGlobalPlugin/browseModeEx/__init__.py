# globalPlugins\NVDAExtensionGlobalPlugin\browseModeEx\__init__.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2016 - 2023 paulber19
# This file is covered by the GNU General Public License.


import addonHandler
from cursorManager import CursorManager
import NVDAObjects.UIA.spartanEdge as EDGE
import NVDAObjects.IAccessible.MSHTML
import NVDAObjects.IAccessible.mozilla
import NVDAObjects.IAccessible.chromium
import NVDAObjects.UIA.chromium

import browseMode
from inputCore import SCRCAT_BROWSEMODE
from scriptHandler import getLastScriptRepeatCount, willSayAllResume
import winsound
import speech
import ui
import textInfos
import api
import config
from versionInfo import version_year, version_major
NVDAVersion = [version_year, version_major]
if NVDAVersion >= [2022, 4]:
	# for nvda version >= 2022.4
	from .documentBaseEx import DocumentWithTableNavigation_2022_4 as DocumentWithTableNavigationEx
elif NVDAVersion > [2022, 1]:
	# for nvda version >= 2022.2
	from .documentBaseEx import DocumentWithTableNavigation_2022_2 as DocumentWithTableNavigationEx
else:
	# for nvda versions until 2022.1
	from .documentBaseEx import DocumentWithTableNavigation_2022_1 as DocumentWithTableNavigationEx
from .. utils import delayScriptTask, stopDelayScriptTask, clearDelayScriptTask
from ..utils.NVDAStrings import NVDAString
from ..settings import toggleLoopInNavigationModeOption

addonHandler.initTranslation()
# Add new quick navigation keys and scripts.
qn = browseMode.BrowseModeTreeInterceptor.addQuickNav
qn(
	"paragraph", key="p",
	# Translators: Input help message for a quick navigation command
	# in browse mode.
	nextDoc=_("moves to the next paragraph"),
	# Translators: Message presented when the browse mode element is not found.
	nextError=_("no next paragraph"),
	# Translators: Input help message for a quick navigation command
	# in browse mode.
	prevDoc=_("moves to the previous paragraph"),
	# Translators: Message presented when the browse mode element is not found.
	prevError=_("no previous paragraph"),
	readUnit=textInfos.UNIT_PARAGRAPH)
qn(
	"division", key="y",
	# Translators: Input help message for a quick navigation command
	# in browse mode.
	nextDoc=_("moves to the next division"),
	# Translators: Message presented when the browse mode element is not found.
	nextError=_("no next division"),
	# Translators: Input help message for a quick navigation command
	# in browse mode.
	prevDoc=_("moves to the previous division"),
	# Translators: Message presented when the browse mode element is not found.
	prevError=_("no previous division"),
	readUnit=textInfos.UNIT_LINE)
qn(
	"mainLandmark", key=";",
	# Translators: Input help message for a quick navigation command
	# in browse mode.
	nextDoc=_("moves to the next main landmark"),
	# Translators: Message presented when the browse mode element is not found.
	nextError=_("no next main landmark"),
	# Translators: Input help message for a quick navigation command
	# in browse mode.
	prevDoc=_("moves to the previous main landmark"),
	# Translators: Message presented when the browse mode element is not found.
	prevError=_("no previous main landmark"),
	readUnit=textInfos.UNIT_LINE)

qn(
	"clickable", key=":",
	# Translators: Input help message for a quick navigation command
	# in browse mode.
	nextDoc=_("moves to the next clickable element"),
	# Translators: Message presented when the browse mode element is not found.
	nextError=_("no next clickable element"),
	# Translators: Input help message for a quick navigation command
	# in browse mode.
	prevDoc=_("moves to the previous clickable element"),
	# Translators: Message presented when the browse mode element is not found.
	prevError=_("no previous clickable element"),
	readUnit=textInfos.UNIT_PARAGRAPH)
del qn


class CursorManagerEx(CursorManager):
	# we want to ear symbols and punctuation when moving by word
	def _caretMovementScriptHelper(
		self, gesture, unit, *args, **kwargs):

		curLevel = config.conf["speech"]["symbolLevel"]
		if unit == textInfos.UNIT_WORD:
			from ..settings.nvdaConfig import _NVDAConfigManager
			symbolLevelOnWordCaretMovement = _NVDAConfigManager .getSymbolLevelOnWordCaretMovement()
			if symbolLevelOnWordCaretMovement is not None:
				config.conf["speech"]["symbolLevel"] = symbolLevelOnWordCaretMovement
		super(CursorManagerEx, self)._caretMovementScriptHelper(
			gesture, unit, *args, **kwargs)
		config.conf["speech"]["symbolLevel"] = curLevel


class BrowseModeDocumentTreeInterceptorEx(
	DocumentWithTableNavigationEx,
	CursorManagerEx, browseMode.BrowseModeDocumentTreeInterceptor):
	_myGestureMap = {
		"kb(desktop):nvda+a": "reportDocumentConstantIdentifier",
		"kb(laptop):nvda+shift+a": "reportDocumentConstantIdentifier",
	}

	def __init__(self, rootNVDAObject):
		super(BrowseModeDocumentTreeInterceptorEx, self).__init__(rootNVDAObject)
		self.bindGestures(BrowseModeDocumentTreeInterceptorEx._myGestureMap)

	def script_reportDocumentConstantIdentifier(self, gesture):
		def callback(toClip=False):
			clearDelayScriptTask()
			text = self._get_documentConstantIdentifier()
			if not text:
				return
			if not toClip:
				ui.message(text)
			else:
				if api.copyToClip(text):
					msg = text
					if len(text) > 35:
						tempList = text[:35].split("/")
						tempList[-1] = "..."
						msg = "/".join(tempList)
					ui.message(msg)
					# Translators: message presented when the text is copied to the clipboard.
					speech.speakMessage(_("Copied to clipboard"))
				else:
					# Translators: message presented when the text cannot be
					# copied to the clipboard.
					speech.speakMessage(_("Cannot copy to clipboard"))
		stopDelayScriptTask()
		if getLastScriptRepeatCount() == 0:
			delayScriptTask(callback, False)
		else:
			callback(True)

	# Translators: Input help mode message
# for report Document Constant Identifier command.
	script_reportDocumentConstantIdentifier.__doc__ = _(
		"Report document 's address (URL). Twice: copy it to clipboard")
	script_reportDocumentConstantIdentifier.category = SCRCAT_BROWSEMODE

	def _quickNavScript(
		self, gesture, itemType, direction, errorMessage, readUnit):
		if itemType == "notLinkBlock":
			iterFactory = self._iterNotLinkBlock
		else:
			iterFactory = lambda direction, info: self._iterNodesByType(
				itemType, direction, info)
		info = self.selection
		try:
			item = next(iterFactory(direction, info))
		except NotImplementedError:
			# Translators: a message when a particular quick nav command
			# is not supported in the current document.
			ui.message(NVDAString("Not supported in this document"))
			return
		except StopIteration:
			if not toggleLoopInNavigationModeOption(False):
				ui.message(errorMessage)
				return
			# return to the top or bottom of page and continue search
			if direction == "previous":
				info = api.getReviewPosition().obj.makeTextInfo(textInfos.POSITION_LAST)
				self._set_selection(info, reason="quickNav")
				# Translators: message to the user which indicates the return
				# to the bottom of the page.
				msg = _("Return to bottom of page")
			else:
				info = None
				# Translators: message to user which indicates the return
				# to the top of the page.
				msg = _("Return to top of page")
			try:
				item = next(iterFactory(direction, info))
			except Exception:
				ui.message(errorMessage)
				return
			ui.message(msg)
			winsound.PlaySound("default", 1)
		# #8831: Report before moving because moving might change the focus, which
		# might mutate the document, potentially invalidating info if it is
		# offset-based.
		if not gesture or not willSayAllResume(gesture):
			item.report(readUnit=readUnit)
		item.moveTo()


def chooseNVDAObjectOverlayClasses(obj, clsList):
	if EDGE.EdgeHTMLRoot in clsList:
		from .NVDAObjectsUIA import EdgeHTMLRootEx
		clsList[clsList.index(EDGE.EdgeHTMLRoot)] = EdgeHTMLRootEx
		return
	if NVDAObjects.IAccessible.MSHTML.MSHTML in clsList:
		from . import NVDAObjectsIAccessible
		clsList[clsList.index(NVDAObjects.IAccessible.MSHTML.MSHTML)] = NVDAObjectsIAccessible.NVDAObjectMSHTMLEx
		return
	if NVDAObjects.IAccessible.mozilla.Document in clsList:
		from . import NVDAObjectsIAccessible
		clsList[clsList.index(
			NVDAObjects.IAccessible.mozilla.Document)] = NVDAObjectsIAccessible.NVDAObjectMozillaDocumentEx
		return
	if NVDAObjects.IAccessible.chromium.Document in clsList:
		from . import NVDAObjectsIAccessible
		clsList[clsList.index(NVDAObjects.IAccessible.chromium.Document)] = NVDAObjectsIAccessible.ChromiumDocument
		return
	if NVDAObjects.UIA.chromium.ChromiumUIADocument in clsList:
		from . import NVDAObjectsUIAChromium
		newCls = NVDAObjectsUIAChromium.ChromiumUIADocumentEx
		clsList[clsList.index(NVDAObjects.UIA.chromium.ChromiumUIADocument)] = newCls
