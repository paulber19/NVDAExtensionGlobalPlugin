# globalPlugins\NVDAExtensionGlobalPlugin\browseModeEx\browseModeUIAEx.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2016 - 2022 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import addonHandler
from ctypes import byref
from comtypes import COMError
from comtypes.automation import VARIANT
try:
	# for nvda version >= 2021.2
	from controlTypes.role import _roleLabels as roleLabels
	from controlTypes.role import Role
	ROLE_CHECKBOX = Role.CHECKBOX
	from controlTypes.state import _stateLabels as stateLabels
	from controlTypes.state import _negativeStateLabels as negativeStateLabels
	from controlTypes.state import State
	STATE_CHECKED = State.CHECKED
except (ModuleNotFoundError, AttributeError):
	from controlTypes import roleLabels
	from controlTypes import stateLabels
	from controlTypes import ROLE_CHECKBOX
	from controlTypes import STATE_CHECKED
	from controlTypes import negativeStateLabels
try:
	# for nvda version >= 2022.1
	import UIAHandler.browseMode as UIABrowseMode
	from UIAHandler.utils import isUIAElementInWalker, getDeepestLastChildUIAElementInWalker
	from UIAHandler.browseMode import UIABrowseModeDocument
except ImportError:
	import UIABrowseMode
	from UIAUtils import isUIAElementInWalker, getDeepestLastChildUIAElementInWalker
	from UIABrowseMode import UIABrowseModeDocument

import UIAHandler


from .__init__ import BrowseModeDocumentTreeInterceptorEx
from . import elementsList
from . import UIAParagraph
from ..utils.NVDAStrings import NVDAString

addonHandler.initTranslation()


class UIATextRangeQuickNavItemEx(UIABrowseMode .UIATextRangeQuickNavItem):
	@property
	def label(self):
		value = super(UIATextRangeQuickNavItemEx, self).label
		obj = self.obj
		# Translators: label when object has no name.
		name = obj.name if obj.name else _("No label")
		if (self.itemType == "edit"):
			value = str("{name} {role} {value}") .format(
				name=name, role=roleLabels[obj.role], value=value)
		elif self.itemType == "checkBox":
			if STATE_CHECKED in obj.states:
				state = stateLabels[STATE_CHECKED]
			else:
				state = negativeStateLabels[STATE_CHECKED]
			value = str("{name} {state}") .format(name=name, state=state)
		elif self.itemType == "formField":
			if obj.role == ROLE_CHECKBOX:
				if STATE_CHECKED in obj.states:
					state = stateLabels[STATE_CHECKED]
				else:
					state = negativeStateLabels[STATE_CHECKED]
				value = str("{name} {state}") .format(name=name, state=state)
		return value


def UIAControlQuicknavIteratorEx(
	itemType,
	document,
	position,
	UIACondition,
	direction="next",
	itemClass=UIATextRangeQuickNavItemEx):
	# A part from the condition given,
	# we must always match on the root of the document
	# so we know when to stop walking
	runtimeID = VARIANT()
	document.rootNVDAObject.UIAElement._IUIAutomationElement__com_GetCurrentPropertyValue(
		UIAHandler.UIA_RuntimeIdPropertyId, byref(runtimeID))
	UIACondition = UIAHandler.handler.clientObject.createOrCondition(
		UIAHandler.handler.clientObject.createPropertyCondition(
			UIAHandler.UIA_RuntimeIdPropertyId, runtimeID),
		UIACondition)
	if not position:
		# All items are requested (such as for elements list)
		elements = document.rootNVDAObject.UIAElement.findAll(
			UIAHandler.TreeScope_Descendants, UIACondition)
		if elements:
			for index in range(elements.length):
				element = elements.getElement(index)
				try:
					elementRange = document.rootNVDAObject.UIATextPattern.rangeFromChild(element)
				except COMError:
					elementRange = None
				if elementRange:
					yield itemClass(itemType, document, elementRange)
		return
	if direction == "up":
		walker = UIAHandler.handler.clientObject.createTreeWalker(UIACondition)
		element = position.UIAElementAtStart
		while element:
			element = walker.normalizeElement(element)
			if (
				not element
				or UIAHandler.handler.clientObject.compareElements(
					element, document.rootNVDAObject.UIAElement)
				or UIAHandler.handler.clientObject.compareElements(
					element, UIAHandler.handler.rootElement)
			):
				break
			try:
				yield itemClass(itemType, document, element)
			except ValueError:
				pass  # this element was not represented in the document's text content.
			element = walker.getParentElement(element)
		return
	elif direction == "previous":
		# Fetching items previous to the given position.
		# When getting children of a UIA text range,
		# Edge will incorrectly include a child that starts at the end of the range.
		# Therefore move back by one character to stop this.
		toPosition = position._rangeObj.clone()
		toPosition.move(UIAHandler.TextUnit_Character, -1)
		child = toPosition.getEnclosingElement()
		childRange = document.rootNVDAObject.UIATextPattern.rangeFromChild(child)
		toPosition.MoveEndpointByRange(
			UIAHandler.TextPatternRangeEndpoint_Start,
			childRange,
			UIAHandler.TextPatternRangeEndpoint_Start)
		# Fetch the last child of this text range.
		# But if its own range extends beyond the end of our position:
		# We know that the child is not the deepest descendant,
		# And therefore we Limit our children fetching range
		# to the start of this child,
		# And fetch the last child again.
		zoomedOnce = False
		while True:
			children = toPosition.getChildren()
			length = children.length
			if length == 0:
				if zoomedOnce:
					child = toPosition.getEnclosingElement()
				break
			child = children.getElement(length - 1)
			try:
				childRange = document.rootNVDAObject.UIATextPattern.rangeFromChild(child)
			except COMError:
				return
			if childRange.CompareEndpoints(
				UIAHandler.TextPatternRangeEndpoint_End,
				position._rangeObj,
				UIAHandler.TextPatternRangeEndpoint_End) > 0 and\
				childRange.CompareEndpoints(
					UIAHandler.TextPatternRangeEndpoint_Start,
					toPosition,
					UIAHandler.TextPatternRangeEndpoint_Start) > 0:
				toPosition.MoveEndpointByRange(
					UIAHandler.TextPatternRangeEndpoint_Start,
					childRange,
					UIAHandler.TextPatternRangeEndpoint_Start)
				zoomedOnce = True
				continue
			break
		if not child or UIAHandler.handler.clientObject.compareElements(
			child, document.rootNVDAObject.UIAElement):
			# We're on the document itself -- probably nothing in it.
			return
		# Work out if this child is previous to our position or not.
		# If it isn't, then we know we still need to move parent
			# or previous before it is safe to emit an item.
		try:
			childRange = document.rootNVDAObject.UIATextPattern.rangeFromChild(child)
		except COMError:
			return
		gonePreviousOnce = childRange.CompareEndpoints(
			UIAHandler.TextPatternRangeEndpoint_End,
			position._rangeObj,
			UIAHandler.TextPatternRangeEndpoint_Start) <= 0
		walker = UIAHandler.handler.clientObject.createTreeWalker(UIACondition)
		curElement = child
		# Start traversing from this child backward through the document,
		# emitting items for valid elements.
		curElementMatchedCondition = False
		goneParent = False
		while curElement:
			if gonePreviousOnce and not goneParent:
				lastChild = getDeepestLastChildUIAElementInWalker(curElement, walker)
				if lastChild:
					curElement = lastChild
					curElementMatchedCondition = True
				elif not curElementMatchedCondition and\
					isUIAElementInWalker(curElement, walker):
					curElementMatchedCondition = True
				if curElementMatchedCondition:
					yield itemClass(itemType, document, curElement)
			previousSibling = walker.getPreviousSiblingElement(curElement)
			if previousSibling:
				gonePreviousOnce = True
				goneParent = False
				curElement = previousSibling
				curElementMatchedCondition = True
				continue
			parent = walker.getParentElement(curElement)
			if parent and not UIAHandler.handler.clientObject.compareElements(
				document.rootNVDAObject.UIAElement, parent):
				curElement = parent
				goneParent = True
				curElementMatchedCondition = True
				if gonePreviousOnce:
					yield itemClass(itemType, document, curElement)
				continue
			curElement = None
	else:  # direction is next
		# Fetching items after the given position.
		# Extend the end of the range forward
		# to the end of the document so that we will be able
		# to fetch children from this point onwards.
		# Fetch the first child of this text range.
		# But if its own range extends before the start of our position:
		# We know that the child is not the deepest descendant,
		# And therefore we Limit our children fetching range
		# to the end of this child,
		# And fetch the first child again.
		child = position._rangeObj.getEnclosingElement()
		childRange = document.rootNVDAObject.UIATextPattern.rangeFromChild(child)
		toPosition = position._rangeObj.clone()
		toPosition.MoveEndpointByRange(
			UIAHandler.TextPatternRangeEndpoint_End,
			childRange,
			UIAHandler.TextPatternRangeEndpoint_End)
		zoomedOnce = False
		while True:
			children = toPosition.getChildren()
			length = children.length
			if length == 0:
				if zoomedOnce:
					child = toPosition.getEnclosingElement()
				break
			child = children.getElement(0)
			try:
				childRange = document.rootNVDAObject.UIATextPattern.rangeFromChild(child)
			except COMError:
				return
			if childRange.CompareEndpoints(
				UIAHandler.TextPatternRangeEndpoint_Start,
				position._rangeObj,
				UIAHandler.TextPatternRangeEndpoint_Start) < 0\
				and childRange.CompareEndpoints(
					UIAHandler.TextPatternRangeEndpoint_End,
					toPosition, UIAHandler.TextPatternRangeEndpoint_End) < 0:
				toPosition.MoveEndpointByRange(
					UIAHandler.TextPatternRangeEndpoint_End,
					childRange,
					UIAHandler.TextPatternRangeEndpoint_End)
				zoomedOnce = True
				continue
			break
		# Work out if this child is after our position or not.
		if not child or UIAHandler.handler.clientObject.compareElements(
			child, document.rootNVDAObject.UIAElement):
			# We're on the document itself -- probably nothing in it.
			return
		try:
			childRange = document.rootNVDAObject.UIATextPattern.rangeFromChild(child)
		except COMError:
			return
		goneNextOnce = childRange.CompareEndpoints(
			UIAHandler.TextPatternRangeEndpoint_Start,
			position._rangeObj,
			UIAHandler.TextPatternRangeEndpoint_Start) > 0
		walker = UIAHandler.handler.clientObject.createTreeWalker(UIACondition)
		curElement = child
		# If we are already past our position, and this is a valid child
		# Then we can emit an item already
		if goneNextOnce and isUIAElementInWalker(curElement, walker):
			yield itemClass(itemType, document, curElement)
		# Start traversing from this child forwards
			# through the document, emitting items for valid elements.
		while curElement:
			firstChild = walker.getFirstChildElement(
				curElement) if goneNextOnce else None
			if firstChild:
				curElement = firstChild
				yield itemClass(itemType, document, curElement)
			else:
				nextSibling = None
				while not nextSibling:
					nextSibling = walker.getNextSiblingElement(curElement)
					if not nextSibling:
						parent = walker.getParentElement(curElement)
						if parent and not UIAHandler.handler.clientObject.compareElements(
							document.rootNVDAObject.UIAElement, parent):
							curElement = parent
						else:
							return
				curElement = nextSibling
				goneNextOnce = True
				yield itemClass(itemType, document, curElement)


UIABrowseMode .UIAControlQuicknavIterator = UIAControlQuicknavIteratorEx


class UIABrowseModeDocumentEx(
	BrowseModeDocumentTreeInterceptorEx, UIABrowseModeDocument):
	def _iterNodesByType(self, nodeType, direction="next", pos=None):
		if nodeType == "paragraph":
			return UIAParagraph.UIAParagraphQuicknavIterator(self, pos, direction)
		if nodeType == "mainLandmark":
			cond1 = UIAHandler.handler.clientObject.createNotCondition(
				UIAHandler.handler.clientObject.createPropertyCondition(
					UIAHandler.UIA_LandmarkTypePropertyId, 0))
			cond2 = UIAHandler.handler.clientObject.createPropertyCondition(
				UIAHandler.UIA_AriaRolePropertyId, "main")
			condition = UIAHandler.handler.clientObject.CreateAndCondition(cond1, cond2)
			return UIAControlQuicknavIteratorEx(
				nodeType, self, pos, condition, direction)
		return super(UIABrowseModeDocumentEx, self)._iterNodesByType(
			nodeType, direction, pos)


class EdgeElementsListDialog(elementsList.ElementsListDialogEx):
	ELEMENT_TYPES = (
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("link", NVDAString("link").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("heading", NVDAString("heading").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("formField", _("Form field")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("button", NVDAString("button").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("landmark", NVDAString("landmark").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("radioButton", NVDAString("radio button").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("paragraph", NVDAString("paragraph").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("checkBox", NVDAString("check box").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("comboBox", NVDAString("combo box").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("table", NVDAString("table").capitalize()),
		# ("blockQuote", NVDAString("block quote").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("edit", NVDAString("edit").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("list", NVDAString("list").capitalize()),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("graphic", NVDAString("graphic").capitalize()),
		# ("embeddedObject", _("Embedded object")),
		# Translators: The label of a list item to select the type of element
		# in the browse mode Elements List dialog.
		("separator", NVDAString("separator").capitalize())
	)
