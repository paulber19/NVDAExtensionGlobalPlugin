# globalPlugins\NVDAExtensionGlobalPlugin\browseModeEx\NVDAObjectsUIAChromium.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2021 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.


from NVDAObjects.UIA.chromium import ChromiumUIADocument, ChromiumUIATreeInterceptor
from .browseModeUIAEx import UIABrowseModeDocumentEx, EdgeElementsListDialog


class ChromiumUIATreeInterceptorEx(
	UIABrowseModeDocumentEx, ChromiumUIATreeInterceptor):
	def _get_ElementsListDialog(self):
		return EdgeElementsListDialog


class ChromiumUIADocumentEx(ChromiumUIADocument):
	treeInterceptorClass = ChromiumUIATreeInterceptorEx
