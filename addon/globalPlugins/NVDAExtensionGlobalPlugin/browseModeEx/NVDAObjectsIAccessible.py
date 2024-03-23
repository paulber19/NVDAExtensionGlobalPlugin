# globalPlugins\NVDAExtensionGlobalPlugin\browseModeEx\NVDAObjectsIAccessible.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2016 - 2023 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.


from controlTypes.role import Role
from controlTypes.state import State
import NVDAObjects
from .virtualBuffersEx import MSHTMLEx, Gecko_ia2_Ex, ChromeVBufEx
import NVDAObjects.IAccessible.chromium


class NVDAObjectMSHTMLEx(NVDAObjects.IAccessible.MSHTML.MSHTML):
	def _get_treeInterceptorClass(self):
		if self.role in (
			Role.DOCUMENT, Role.APPLICATION, Role.DIALOG)\
			and not self.isContentEditable:
			return MSHTMLEx
		return super(NVDAObjectMSHTMLEx, self).treeInterceptorClass


class NVDAObjectMozillaDocumentEx(NVDAObjects.IAccessible.mozilla .Document):
	def _get_treeInterceptorClass(self):
		if State.EDITABLE not in self.states:
			return Gecko_ia2_Ex
		return super(NVDAObjectMozillaDocumentEx, self).treeInterceptorClass


class ChromiumDocument(NVDAObjects.IAccessible.chromium.Document):
	def _get_treeInterceptorClass(self):
		states = self.states
		if State.EDITABLE not in states\
			and State.BUSY not in states:
			return ChromeVBufEx
		return super(ChromiumDocument, self).treeInterceptorClass
