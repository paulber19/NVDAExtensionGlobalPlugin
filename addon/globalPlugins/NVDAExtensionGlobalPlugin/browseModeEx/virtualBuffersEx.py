# globalPlugins\NVDAExtensionGlobalPlugin\browseModeEx\virtualBuffersEx.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2016 - 2023 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import addonHandler
try:
	# for nvda version >= 2021.2
	from controlTypes.role import _roleLabels as roleLabels
	from controlTypes.role import Role
	ROLE_CHECKBOX = Role.CHECKBOX
	from controlTypes.state import State
	STATE_CHECKED = State.CHECKED
except (ModuleNotFoundError, AttributeError):
	from controlTypes import roleLabels, ROLE_CHECKBOX
	from controlTypes import STATE_CHECKED
import NVDAHelper
import ctypes
import aria
import virtualBuffers
import virtualBuffers.MSHTML
import virtualBuffers.gecko_ia2
# from virtualBuffers import *
from virtualBuffers import (
	VBufStorage_findMatch_notEmpty, VBufStorage_findMatch_word,
	VBufStorage_findDirection_up, VBufStorage_findDirection_back, VBufStorage_findDirection_forward,
	VBufRemote_nodeHandle_t
)
from virtualBuffers import _prepareForFindByAttributes
from NVDAObjects.IAccessible import ia2Web
from comtypes import COMError
from comInterfaces import IAccessible2Lib as IA2
from ..utils.NVDAStrings import NVDAString
from . import elementsList
from .__init__ import BrowseModeDocumentTreeInterceptorEx

addonHandler.initTranslation()


def _iterNodesByAttribsEx(
	obj, attribs, direction="next", pos=None, nodeType=None):
	offset = pos._startOffset if pos else -1
	reqAttrs, regexp = _prepareForFindByAttributes(attribs)
	startOffset = ctypes.c_int()
	endOffset = ctypes.c_int()
	if direction == "next":
		direction = VBufStorage_findDirection_forward
	elif direction == "previous":
		direction = VBufStorage_findDirection_back
	elif direction == "up":
		direction = VBufStorage_findDirection_up
	else:
		raise ValueError("unknown direction: %s" % direction)
	while True:
		try:
			node = VBufRemote_nodeHandle_t()
			NVDAHelper.localLib.VBuf_findNodeByAttributes(
				obj.VBufHandle, offset, direction, reqAttrs, regexp,
				ctypes.byref(startOffset), ctypes.byref(endOffset), ctypes.byref(node))
		except Exception:
			return
		if not node:
			return
		yield VirtualBufferQuickNavItemEx(
			nodeType, obj, node, startOffset.value, endOffset.value)
		offset = startOffset


class VirtualBufferEx (
	BrowseModeDocumentTreeInterceptorEx, virtualBuffers.VirtualBuffer):
	def __init__(self, rootNVDAObject):
		super(VirtualBufferEx, self).__init__(rootNVDAObject)


class MSHTMLEx(VirtualBufferEx, virtualBuffers.MSHTML .MSHTML):
	def __init__(self, rootNVDAObject):
		super(MSHTMLEx, self).__init__(rootNVDAObject)

	def _searchableNewAttribsForNodeType(self, nodeType):
		if nodeType == "paragraph":
			attrs = {"IHTMLDOMNode::nodeName": ["P"]}
		elif nodeType == "anchor":
			attrs = {"IHTMLDOMNode::nodeName": ["ANCHOR"]}
		elif nodeType == "division":
			attrs = {"IHTMLDOMNode::nodeName": ["DIV"]}
		elif nodeType == "mainLandmark":
			attrs = [
				{"HTMLAttrib::role": [VBufStorage_findMatch_word("main")]},
				{"HTMLAttrib::role": [VBufStorage_findMatch_word("main")],
					"name": [VBufStorage_findMatch_notEmpty]},
				{"IHTMLDOMNode::nodeName": [VBufStorage_findMatch_word(
					aria.htmlNodeNameToAriaLandmarkRoles["main"].upper())]}
			]

		else:
			attrs = None
		return attrs

	def _searchableAttribsForNodeType(self, nodeType):
		attrs = self._searchableNewAttribsForNodeType(nodeType)
		if attrs is None:
			attrs = super(MSHTMLEx, self)._searchableAttribsForNodeType(nodeType)
		return attrs

	def _iterNodesByAttribs(
		self, attribs, direction="next", pos=None, nodeType=None):
		return _iterNodesByAttribsEx(self, attribs, direction, pos, nodeType)

	def _get_ElementsListDialog(self):
		return elementsList.ElementsListDialogEx


class Gecko_ia2_Ex(VirtualBufferEx, virtualBuffers.gecko_ia2 .Gecko_ia2):
	def __init__(self, rootNVDAObject):
		super(Gecko_ia2_Ex, self).__init__(rootNVDAObject)

	def _searchableNewAttribsForNodeType(self, nodeType):
		if nodeType == "paragraph":
			attrs = {"IAccessible::role": [IA2.IA2_ROLE_PARAGRAPH]}
		elif nodeType == "division":
			attrs = {"IAccessible2::attribute_tag": self._searchableTagValues(["DIV"])}
		elif nodeType == "anchor":
			attrs = {"IAccessible2::attribute_tag": self._searchableTagValues(["ANCHOR"])}
		elif nodeType == "mainLandmark":
			attrs = [
				{"IAccessible2::attribute_xml-roles": [VBufStorage_findMatch_word("main")]},
				{"IAccessible2::attribute_xml-roles": [VBufStorage_findMatch_word("main")],
					"name": [VBufStorage_findMatch_notEmpty]}
			]
		elif nodeType == "clickable":
			attrs = {"IAccessibleAction_click": ["0"]}
		else:
			attrs = None
		return attrs

	def _searchableAttribsForNodeType(self, nodeType):
		attrs = self._searchableNewAttribsForNodeType(nodeType)
		if attrs is None:
			attrs = super(Gecko_ia2_Ex, self)._searchableAttribsForNodeType(nodeType)
		return attrs

	def _iterNodesByAttribs(
		self, attribs, direction="next", pos=None, nodeType=None):
		return _iterNodesByAttribsEx(self, attribs, direction, pos, nodeType)

	def _get_ElementsListDialog(self):
		return elementsList.GeckoElementsListDialog


class ChromeVBufEx(Gecko_ia2_Ex):
	def __contains__(self, obj):
		if obj.windowHandle != self.rootNVDAObject.windowHandle:
			return False
		if not isinstance(obj, ia2Web.Ia2Web):
			# #4080: Input composition NVDAObjects are the same window
			# but not IAccessible2!
			return False
		accId = obj.IA2UniqueID
		if accId == self.rootID:
			return True
		try:
			self.rootNVDAObject.IAccessibleObject.accChild(accId)
		except COMError:
			return False
		return not self._isNVDAObjectInApplication(obj)


class VirtualBufferQuickNavItemEx(virtualBuffers.VirtualBufferQuickNavItem):
	def getLabel(self, value):
		# Translators: Reported label in the elements list
		# for an element which which has no name and value.
		unlabeled = NVDAString("Unlabeled")
		return value if value and len(value.strip()) else unlabeled

	@property
	def label(self):
		try:
			value = super(VirtualBufferQuickNavItemEx, self).label
		except Exception:
			# to catch lookuperror
			value = None

		try:
			attrs = self.textInfo._getControlFieldAttribs(
				self.vbufFieldIdentifier[0], self.vbufFieldIdentifier[1])
		except Exception:
			return self.getLabel(value)
		role = attrs.get("role", "")
		if (self.itemType == "edit"):
			name = attrs.get("name", "")
			return str("{name} {role} {value}").format(
				name=self.getLabel(name), role=roleLabels[role], value=value)
		if self.itemType == "checkBox":
			states = attrs.get("states", "")
			state = NVDAString("checked") if STATE_CHECKED in states\
				else NVDAString("not checked")
			name = attrs.get("name", "")
			return str("%s %s") % (self.getLabel(name), state)
		if self.itemType in ["formField"]:
			if role == ROLE_CHECKBOX:
				states = attrs.get("states", "")
				state = NVDAString("checked") if STATE_CHECKED in states\
					else NVDAString("not checked")
				name = attrs.get("name", "")
				return str("{name} {role} {state}") .format(
					name=name, role=roleLabels[role], state=state)
			return value
		return self.getLabel(value)
