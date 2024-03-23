# globalPlugins\NVDAExtensionGlobalPlugin\browseModeEx\__init__.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2016 - 2023 paulber19
# This file is covered by the GNU General Public License.


import NVDAObjects.UIA.spartanEdge as EDGE
import NVDAObjects.IAccessible.MSHTML
import NVDAObjects.IAccessible.mozilla
import NVDAObjects.IAccessible.chromium
import NVDAObjects.UIA.chromium


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
