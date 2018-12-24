# NVDAExtensionGlobalPlugin/browseModeEx/NVDAObjectsUIA.py
#A part of NVDAExtensionGlobalPlugin add-on
#Copyright (C) 2016  paulber19
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.

import NVDAObjects.UIA.edge
from browseModeUIAEx import UIABrowseModeDocumentEx, EdgeElementsListDialog


class EdgeHTMLTreeInterceptorEx (UIABrowseModeDocumentEx, NVDAObjects.UIA.edge.EdgeHTMLTreeInterceptor):

	def _get_ElementsListDialog(self):
		return EdgeElementsListDialog


class EdgeHTMLRootEx(NVDAObjects.UIA.edge.EdgeHTMLRoot):
	treeInterceptorClass=EdgeHTMLTreeInterceptorEx

