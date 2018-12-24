# NVDAExtensionGlobalPlugin/browseModeEx/NVDAObjectsIAccessible.py
#A part of NVDAExtensionGlobalPlugin add-on
#Copyright (C) 2016 - 2017 paulber19
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.

import controlTypes
import NVDAObjects
from virtualBuffersEx import MSHTMLEx, Gecko_ia2Pre14Ex, Gecko_ia2_Ex, ChromeVBufEx

class NVDAObjectMSHTMLEx(NVDAObjects.IAccessible.MSHTML.MSHTML):
	def _get_treeInterceptorClass(self):
		if self.role in (controlTypes.ROLE_DOCUMENT, controlTypes.ROLE_APPLICATION, controlTypes.ROLE_DIALOG) and not self.isContentEditable:
			return MSHTMLEx
		return super(NVDAObjectMSHTMLEx,self).treeInterceptorClass
		
class NVDAObjectMozillaDocumentEx(NVDAObjects.IAccessible.mozilla .Document):
	
	def _get_treeInterceptorClass(self):
		ver=NVDAObjects.IAccessible.mozilla.getGeckoVersion(self)
		if (not ver or ver.full.startswith('1.9')) and self.windowClassName!="MozillaContentWindowClass":
			return super(NVDAObjectMozillaDocumentEx,self).treeInterceptorClass
		if controlTypes.STATE_EDITABLE not in self.states:
			if ver and ver.major < 14:
				return Gecko_ia2Pre14Ex
			else:
				return Gecko_ia2_Ex
		return super(NVDAObjectMozillaDocumentEx,self).treeInterceptorClass

import NVDAObjects.IAccessible.chromium

class ChromiumDocument(NVDAObjects.IAccessible.chromium.Document):
	def _get_treeInterceptorClass(self):
		states = self.states
		if controlTypes.STATE_EDITABLE not in states and controlTypes.STATE_BUSY not in states:
			return ChromeVBufEx
		return super(ChromiumDocument, self).treeInterceptorClass

		