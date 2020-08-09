# NVDAExtensionGlobalPlugin/browseModeEx/NVDAObjectsIAccessible.py
#A part of NVDAExtensionGlobalPlugin add-on
#Copyright (C) 2016 - 2017 paulber19
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.

import controlTypes
import NVDAObjects
from .virtualBuffersEx import MSHTMLEx, Gecko_ia2_Ex, ChromeVBufEx
from . import virtualBuffersEx


class NVDAObjectMSHTMLEx(NVDAObjects.IAccessible.MSHTML.MSHTML):
	def _get_treeInterceptorClass(self):
		if self.role in (controlTypes.ROLE_DOCUMENT, controlTypes.ROLE_APPLICATION, controlTypes.ROLE_DIALOG) and not self.isContentEditable:
			return MSHTMLEx
		return super(NVDAObjectMSHTMLEx,self).treeInterceptorClass
		
class NVDAObjectMozillaDocumentEx(NVDAObjects.IAccessible.mozilla .Document):
	
	def _get_treeInterceptorClass(self):
		if controlTypes.STATE_EDITABLE not in self.states:
			return Gecko_ia2_Ex
		return super(NVDAObjectMozillaDocumentEx,self).treeInterceptorClass

import NVDAObjects.IAccessible.chromium

class ChromiumDocument(NVDAObjects.IAccessible.chromium.Document):
	def _get_treeInterceptorClass(self):
		states = self.states
		if controlTypes.STATE_EDITABLE not in states and controlTypes.STATE_BUSY not in states:
			return ChromeVBufEx
		return super(ChromiumDocument, self).treeInterceptorClass

