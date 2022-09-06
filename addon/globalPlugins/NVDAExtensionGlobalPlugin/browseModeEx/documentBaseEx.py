# globalPlugins\NVDAExtensionGlobalPlugin\browseModeEx\documentBaseEx.py
# a part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2018 - 2022 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import addonHandler
import documentBase
from ..utils.NVDAStrings import NVDAString
import config
import controlTypes
try:
	# fornvda version >=  2020.1
	from controlTypes import OutputReason
	REASON_MESSAGE = OutputReason.MESSAGE
	REASON_CARET = OutputReason.CARET
	REASON_QUERY = OutputReason.QUERY
except ImportError:
	REASON_MESSAGE = controlTypes.REASON_MESSAGE
	REASON_CARET = controlTypes.REASON_CARET
	REASON_QUERY = controlTypes.REASON_QUERY

addonHandler.initTranslation()

SCRCAT_TABLE = NVDAString("table").capitalize()


class _DocumentWithTableNavigationBase(documentBase.DocumentWithTableNavigation):
	_myGestureMap = {
		"kb(desktop):nvda+alt+numpad5": "reportCurrentCellPosition",
		"kb(laptop):nvda+alt+;": "reportCurrentCellPosition",
		"kb:nvda+alt+j": "reportCurrentRow",
		"kb:nvda+alt+l": "reportCurrentColumn",
		"kb:nvda+alt+downArrow": "moveToAndReportNextRow",
		"kb:nvda+alt+upArrow": "moveToAndReportPreviousRow",
		"kb:nvda+alt+rightArrow": "moveToAndReportNextColumn",
		"kb:nvda+alt+leftArrow": "moveToAndReportPreviousColumn",
	}

	def __init__(self, rootNVDAObject):
		super(_DocumentWithTableNavigationBase, self).__init__(rootNVDAObject)
		self.bindGestures(_DocumentWithTableNavigationBase._myGestureMap)
		# set category of NVDA base table scripts to SCRCAT_TABLE
		documentBase.DocumentWithTableNavigation.script_nextRow.category = SCRCAT_TABLE
		documentBase.DocumentWithTableNavigation.script_previousRow.category = SCRCAT_TABLE
		documentBase.DocumentWithTableNavigation.script_nextColumn.category = SCRCAT_TABLE
		documentBase.DocumentWithTableNavigation.script_previousColumn.category = SCRCAT_TABLE

	def _reportRowOrColumn(self, axis="row"):
		# documentBase is a core module and should not depend on UI, so it is imported at run-time. (#12404)
		import ui
		from speech import speakTextInfo
		try:
			tableID, origRow, origCol, origRowSpan, origColSpan = self._getTableCellCoords(self.selection)
			(row, col) = (origRow, 1) if axis == "row" else (1, origCol)
			info = self._getTableCellAt(tableID, self.selection, row, col)
		except LookupError:
			# Translators: The message reported when a user attempts
			# to use a table report command.
			# when the cursor is not within a table.
			ui.message(NVDAString("Not in a table cell"))
			return
		formatConfig = config.conf["documentFormatting"].copy()
		formatConfig["reportTables"] = True
		formatConfig["includeLayoutTables"] = True
		formatConfig["reportTableCellCoords"] = True
		while info:
			_ignore, row, col, rowSpan, colSpan = self._getTableCellCoords(info)
			if axis == "row" and row != origRow:
				break
			elif axis == "column" and col != origCol:
				pass
			else:
				speakTextInfo(
					info, formatConfig=formatConfig, reason=REASON_MESSAGE)
			try:
				if axis == "row":
					info = self._getNearestTableCell(
						tableID,
						info,
						origRow=row, origCol=col,
						origRowSpan=rowSpan, origColSpan=colSpan,
						movement="next",
						axis="column")
				else:
					info = self._getNearestTableCell(
						tableID,
						info, origRow=row,
						origCol=col,
						origRowSpan=rowSpan,
						origColSpan=colSpan,
						movement="next",
						axis="row")
			except LookupError:
				break

	def script_reportCurrentRow(self, gesture):
		# documentBase is a core module and should not depend on these UI modules and so they are imported
		# at run-time. (#12404)
		from scriptHandler import isScriptWaiting
		if isScriptWaiting():
			return
		self._reportRowOrColumn(axis="row")
	# Translators: Input help mode message for report Current Row command.
	script_reportCurrentRow.__doc__ = _("Report current table row's cells")
	script_reportCurrentRow.category = SCRCAT_TABLE

	def script_reportCurrentColumn(self, gesture):
		# documentBase is a core module and should not depend on these UI modules and so they are imported
		# at run-time. (#12404)
		from scriptHandler import isScriptWaiting
		if isScriptWaiting():
			return
		self._reportRowOrColumn(axis="column")
	# Translators: Input help mode message for report Current column command.
	script_reportCurrentColumn.__doc__ = _("Report current table column's cells")
	script_reportCurrentColumn.category = SCRCAT_TABLE

	def moveToAndReportTableElement(self, element="row", direction="next"):
		# documentBase is a core module and should not depend on these UI modules and so they are imported
		# at run-time. (#12404)
		from scriptHandler import isScriptWaiting
		import ui
		if isScriptWaiting():
			return
		try:
			tableID, origRow, origCol, origRowSpan, origColSpan = self._getTableCellCoords(self.selection)
			(row, col) = (origRow, 1) if element == "row" else (1, origCol)
		except LookupError:
			# Translators: The message reported when a user attempts
			# to use a table report command.
			# when the cursor is not within a table.
			ui.message(NVDAString("Not in a table cell"))
			return
		self._tableMovementScriptHelper(movement=direction, axis=element)
		self._reportRowOrColumn(axis=element)

	def script_moveToAndReportNextRow(self, gesture):
		self.moveToAndReportTableElement("row", "next")
	# Translators: Input help mode message
		# to move To And Report Next Row command.
	script_moveToAndReportNextRow.__doc__ = _("Move to and report next table row")
	script_moveToAndReportNextRow.category = SCRCAT_TABLE

	def script_moveToAndReportPreviousRow(self, gesture):
		self.moveToAndReportTableElement("row", "previous")
	# Translators: Input help mode message
		# to move To And Report previous Row command.
	script_moveToAndReportPreviousRow.__doc__ = _("Move to and report previous table row")
	script_moveToAndReportPreviousRow	.category = SCRCAT_TABLE

	def script_moveToAndReportNextColumn(self, gesture):
		self.moveToAndReportTableElement("column", "next")
	# Translators: Input help mode message
		# to move To And Report Next column command.
	script_moveToAndReportNextColumn.__doc__ = _("Move to and report next table column")
	script_moveToAndReportNextColumn	.category = SCRCAT_TABLE

	def script_moveToAndReportPreviousColumn(self, gesture):
		self.moveToAndReportTableElement("column", "previous")
	# Translators: Input help mode message
		# to move To And Report previous column command.
	script_moveToAndReportPreviousColumn.__doc__ = _("Move to and report previous table column")
	script_moveToAndReportPreviousColumn	.category = SCRCAT_TABLE

	def _reportCurrentCellPosition(self):
		# documentBase is a core module and should not depend on UI, so it is imported at run-time. (#12404)
		import ui
		from speech import speakTextInfo
		try:
			tableID, row, col, rowSpan, colSpan = self._getTableCellCoords(self.selection)
			info = self._getTableCellAt(tableID, self.selection, row, col)
		except LookupError:
			# Translators: The message reported when a user attempts
			# to use a table report command.
			# when the cursor is not within a table.
			ui.message(NVDAString("Not in a table cell"))
			return
		formatConfig = config.conf["documentFormatting"].copy()
		formatConfig["reportTables"] = False
		formatConfig["reportTableHeaders"] = True
		formatConfig["includeLayoutTables"] = True
		formatConfig["reportTableCellCoords"] = True
		speakTextInfo(
			info,
			useCache=False,
			formatConfig=formatConfig,
			reason=REASON_QUERY, onlyInitialFields=False)

	def script_reportCurrentCellPosition(self, gesture):
		# documentBase is a core module and should not depend on these UI modules and so they are imported
		# at run-time. (#12404)
		from scriptHandler import isScriptWaiting
		if isScriptWaiting():
			return
		self._reportCurrentCellPosition()
	# Translators: Input help mode message
	# to report current cell position command.
	script_reportCurrentCellPosition.__doc__ = _("Report current table cell position")
	script_reportCurrentCellPosition	.category = SCRCAT_TABLE


# for nvda 2022.2 and higher
# nvda 2022.2 adds new table scriptsto move to first and last row/column.
# so this scripts are removed from the add-on for this nvda version  and  higher
class DocumentWithTableNavigation_2022_2(_DocumentWithTableNavigationBase):
	def __init__(self, rootNVDAObject):
		super(DocumentWithTableNavigation_2022_2, self).__init__(rootNVDAObject)
		# set category of new NVDA base table scripts to SCRCAT_TABLE
		documentBase.DocumentWithTableNavigation.script_firstRow.category = SCRCAT_TABLE
		documentBase.DocumentWithTableNavigation.script_lastRow.category = SCRCAT_TABLE
		documentBase.DocumentWithTableNavigation.script_firstColumn.category = SCRCAT_TABLE
		documentBase.DocumentWithTableNavigation.script_lastColumn.category = SCRCAT_TABLE


# until nvda 2022.1
class DocumentWithTableNavigation_2022_1(_DocumentWithTableNavigationBase):
	_myGestureMap = {
		"kb:control+alt+shift+leftArrow": "moveToFirstCellOfRow",
		"kb:control+alt+shift+rightArrow": "moveToLastCellOfRow",
		"kb:control+alt+shift+upArrow": "moveToFirstCellOfColumn",
		"kb:control+alt+shift+downArrow": "moveToLastCellOfColumn",
	}

	def __init__(self, rootNVDAObject):
		super(DocumentWithTableNavigation_2022_1, self).__init__(rootNVDAObject)
		self.bindGestures(DocumentWithTableNavigation_2022_1._myGestureMap)

	def script_moveToFirstCellOfRow(self, gesture):
		self._tableMovementFirstOrLastScriptHelper(axis="column", movement="first")
	# Translators: Input help mode message for move To first cell of row command.
	script_moveToFirstCellOfRow.__doc__ = _("Move to first cell of table row")
	script_moveToFirstCellOfRow	.category = SCRCAT_TABLE

	def script_moveToLastCellOfRow(self, gesture):
		self._tableMovementFirstOrLastScriptHelper(axis="column", movement="last")
	# Translators: Input help mode message for move To last cell of row command.
	# Translators: Input help mode message to move To last cell of row command.
	script_moveToLastCellOfRow.__doc__ = _("Move to last cell of table row")
	script_moveToLastCellOfRow.category = SCRCAT_TABLE

	def script_moveToFirstCellOfColumn(self, gesture):
		self._tableMovementFirstOrLastScriptHelper(axis="row", movement="first")
	# Translators: Input help mode message
		# for move To first cell of column command.
	script_moveToFirstCellOfColumn.__doc__ = _("Move to first cell of table column")
	script_moveToFirstCellOfColumn	.category = SCRCAT_TABLE

	def script_moveToLastCellOfColumn(self, gesture):
		self._tableMovementFirstOrLastScriptHelper(axis="row", movement="last")
	# Translators: Input help mode message
		# for move To last cell of column command.
	script_moveToLastCellOfColumn.__doc__ = _("Move to last cell of table column")
	script_moveToLastCellOfColumn	.category = SCRCAT_TABLE

	def _tableMovementFirstOrLastScriptHelper(self, movement="first", axis=None):
		# documentBase is a core module and should not depend on these UI modules and so they are imported
		# at run-time. (#12404)
		from scriptHandler import isScriptWaiting
		from speech import speakTextInfo
		import ui
		if isScriptWaiting():
			return
		formatConfig = config.conf["documentFormatting"].copy()
		formatConfig["reportTables"] = True
		formatConfig["includeLayoutTables"] = True
		try:
			tableID, origRow, origCol, origRowSpan, origColSpan = self._getTableCellCoords(
				self.selection)
		except LookupError:
			# Translators: The message reported when a user attempts
			# to use a table movement command.
			# when the cursor is not within a table.
			ui.message(NVDAString("Not in a table cell"))
			return
		direction = "previous" if movement == "first" else "next"
		try:
			info = self._getNearestTableCell(
				tableID,
				self.selection,
				origRow, origCol,
				origRowSpan, origColSpan,
				direction,
				axis)
		except LookupError:
			# Translators: The message reported when a user
			# attempts to use a table movement command.
			# but the cursor can't be moved in that direction
			# because it is at the edge of the table.
			ui.message(NVDAString("Edge of table"))
			# Retrieve the cell on which we started.
			info = self._getTableCellAt(tableID, self.selection, origRow, origCol)
			speakTextInfo(
				info, formatConfig=formatConfig, reason=REASON_CARET)
			info.collapse()
			self.selection = info
			return
		try:
			tableID1, origRow1, origCol1 = tableID, origRow, origCol
			origRowSpan1, origColSpan1 = origRowSpan, origColSpan
			i = 500
			while i > 0:
				i = i - 1
				info = self._getNearestTableCell(
					tableID1,
					self.selection,
					origRow1, origCol1,
					origRowSpan1, origColSpan1,
					direction,
					axis)
				tableID1, origRow1, origCol1, origRowSpan1, origColSpan1 = self._getTableCellCoords(self.selection)
				info.collapse()
				self.selection = info
		except LookupError:
			# Retrieve the previous cell
			info = self._getTableCellAt(tableID1, self.selection, origRow1, origCol1)
		speakTextInfo(
			info, formatConfig=formatConfig, reason=REASON_CARET)
		info.collapse()
		self.selection = info
