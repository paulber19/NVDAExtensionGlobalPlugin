# NVDAExtensionGlobalPlugin/winExplorer/__init__.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2016 - 2022 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import addonHandler
import ui
try:
	# for nvda version >= 2021.2
	from controlTypes.role import Role
	ROLE_TABLEROW = Role.TABLEROW
	ROLE_TREEVIEWITEM = Role.TREEVIEWITEM
	ROLE_TREEVIEW = Role.TREEVIEW,
	ROLE_LIST = Role.LIST
	ROLE_LISTITEM = Role.LISTITEM
	ROLE_DOCUMENT = Role.DOCUMENT
	ROLE_UNKNOWN = Role.UNKNOWN
	from controlTypes.state import State
	STATE_INVISIBLE = State.INVISIBLE
except (ModuleNotFoundError, AttributeError):
	from controlTypes import (
		ROLE_TABLEROW, ROLE_TREEVIEWITEM,
		ROLE_TREEVIEW, ROLE_LIST, ROLE_LISTITEM,
		ROLE_DOCUMENT, ROLE_UNKNOWN,
		STATE_INVISIBLE)
import api
import queueHandler
import itertools
from .elementListDialog import ElementListDialog
from ..utils import runInThread, isOpened
addonHandler.initTranslation()

_generatorID = None
_running = False


def _startGenerator(generator):
	global _generatorID
	stop()
	_generatorID = queueHandler.registerGeneratorObject(generator)


def stop():
	global _generatorID
	if _generatorID is None:
		return
	queueHandler.cancelGeneratorObject(_generatorID)
	_generatorID = None


def isRunning():
	global _running
	ret = _running
	_running = False
	return ret


def generateObjectSubtreeGetObject(obj, indexGen, th):
	global _running
	index = next(indexGen)
	yield obj, index
	rowCount = 0
	treeCount = 0
	listCount = 0
	try:
		# childCount = len(obj.children)
		childCount = obj.childCount
	except Exception:
		childCount = 0
	for i in range(childCount):
		_running = True
		try:
			child = obj.getChild(i)
			if child is None:
				continue
		except Exception:
			continue
		role = child.role
		invisible = STATE_INVISIBLE in child.states
		try:
			childParent = child.parent
			try:
				parentChildCount = childParent.childCount
			except Exception:
				parentChildCount = 0
		except Exception:
			childParent = None
			parentChildCount = 0
		if role == ROLE_TABLEROW:
			if childParent and parentChildCount > 500:
				break
			if invisible:
				continue
			rowCount += 1
			treeCount = 0
			listCount = 0
			if rowCount > 40:
				break
		if role == ROLE_TREEVIEWITEM:
			if childParent and (
				parentChildCount > 500
				or childParent.role not in [ROLE_TREEVIEW, ROLE_LIST]
			):
				break
			if invisible:
				continue
			treeCount += 1
			rowCount = 0
			listCount = 0
			if treeCount > 40:
				break
		if role == ROLE_LISTITEM:
			if childParent and parentChildCount > 500:
				break
			if invisible:
				continue
			listCount += 1
			rowCount = 0
			treeCount = 0
			if listCount > 40:
				break

		if role in [ROLE_DOCUMENT, ]:
			continue
		childGetObject = generateObjectSubtreeGetObject(child, indexGen, th)
		for r in childGetObject:
			_running = True
			yield r


def getObjectsHelper_generator(oParent):
	global _running
	global objectList
	ui.message(_("Elements's searching"))
	objectList = []
	lastSentIndex = 0
	th = runInThread.RepeatBeep(
		delay=2.0, beep=(200, 200), isRunning=isRunning)
	th.start()
	getObjectGen = generateObjectSubtreeGetObject(oParent, itertools.count(), th)
	focus = api.getFocusObject()
	while True:
		_running = True
		if api.getFocusObject() != focus:
			th.stop()
			del th
			return
		try:
			o, lastSentIndex = next(getObjectGen)
			# Consider only objects that are visible on screen and with known role
			if o.role != ROLE_UNKNOWN\
				and STATE_INVISIBLE not in o.states:
				objectList.append(o)
		except StopIteration:
			break
		yield
	_running = True
	th.stop()
	del th
	ElementListDialog.run(oParent, objectList)


def findAllNVDAObjects(oParent):
	if isOpened(ElementListDialog):
		return
	_startGenerator(getObjectsHelper_generator(oParent))
