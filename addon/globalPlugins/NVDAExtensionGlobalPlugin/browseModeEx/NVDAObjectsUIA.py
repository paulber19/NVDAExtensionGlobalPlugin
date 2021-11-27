# globalPlugins\NVDAExtensionGlobalPlugin\browseModeEx\NVDAObjectsUIA.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2016 - 2020 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
try:
	# for nvda version < 2021.1
	from NVDAObjects.UIA.edge import EdgeHTMLRoot, EdgeHTMLTreeInterceptor
except ImportError:
	# for nvda version >= 2021.1
	from NVDAObjects.UIA.spartanEdge import EdgeHTMLRoot, EdgeHTMLTreeInterceptor
from .browseModeUIAEx import UIABrowseModeDocumentEx, EdgeElementsListDialog


class EdgeHTMLTreeInterceptorEx (
	UIABrowseModeDocumentEx, EdgeHTMLTreeInterceptor):
	def _get_ElementsListDialog(self):
		return EdgeElementsListDialog


class EdgeHTMLRootEx(EdgeHTMLRoot):
	treeInterceptorClass = EdgeHTMLTreeInterceptorEx
