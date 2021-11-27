# globalPlugins\NVDAExtensionGlobalPlugin\browseModeEx\NVDAObjectsIAccessible.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2016 - 2021 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

try:
	# for nvda version >= 2021.2
	from controlTypes.role import Role
	ROLE_DOCUMENT = Role.DOCUMENT
	ROLE_APPLICATION = Role.APPLICATION
	ROLE_DIALOG = Role.DIALOG
	from controlTypes.state import State
	STATE_EDITABLE = State.EDITABLE
	STATE_BUSY = State.BUSY
except (ModuleNotFoundError, AttributeError):
	from controlTypes import ROLE_DOCUMENT, ROLE_APPLICATION, ROLE_DIALOG
	from controlTypes import STATE_EDITABLE, STATE_BUSY

import NVDAObjects
from .virtualBuffersEx import MSHTMLEx, Gecko_ia2_Ex, ChromeVBufEx
import NVDAObjects.IAccessible.chromium


class NVDAObjectMSHTMLEx(NVDAObjects.IAccessible.MSHTML.MSHTML):
	def _get_treeInterceptorClass(self):
		if self.role in (
			ROLE_DOCUMENT, ROLE_APPLICATION, ROLE_DIALOG)\
			and not self.isContentEditable:
			return MSHTMLEx
		return super(NVDAObjectMSHTMLEx, self).treeInterceptorClass


class NVDAObjectMozillaDocumentEx(NVDAObjects.IAccessible.mozilla .Document):
	def _get_treeInterceptorClass(self):
		if STATE_EDITABLE not in self.states:
			return Gecko_ia2_Ex
		return super(NVDAObjectMozillaDocumentEx, self).treeInterceptorClass


class ChromiumDocument(NVDAObjects.IAccessible.chromium.Document):
	def _get_treeInterceptorClass(self):
		states = self.states
		if STATE_EDITABLE not in states\
			and STATE_BUSY not in states:
			return ChromeVBufEx
		return super(ChromiumDocument, self).treeInterceptorClass
