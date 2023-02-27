# globalPlugins\NVDAExtensionGlobalPlugin\browseModeEx\documentBaseEx.py
# a part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2018 - 2023 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import addonHandler
import documentBase
from scriptHandler import script

from ..utils.NVDAStrings import NVDAString
import config
from controlTypes import OutputReason


addonHandler.initTranslation()

SCRCAT_TABLE = NVDAString("table").capitalize()


class _DocumentWithTableNavigationBase(documentBase.DocumentWithTableNavigation):
	_myGestureMap = {
		"kb(desktop):nvda+alt+numpad5": "reportCurrentCellPosition",
		"kb(laptop):nvda+alt+;": "reportCurrentCellPosition",
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
					info, formatConfig=formatConfig, reason=OutputReason.MESSAGE)
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

	@script(
		# Translators: Input help mode message for report current table row cells command
		description=_("Report current table row's cells"),
		category=SCRCAT_TABLE,
	)
	def script_reportCurrentRow(self, gesture):
		from scriptHandler import isScriptWaiting
		if isScriptWaiting():
			return
		self._reportRowOrColumn(axis="row")

	@script(
		# Translators: Input help mode message for report current table column cells command
		description=_("Report current table column's cells"),
		category=SCRCAT_TABLE,
	)
	def script_reportCurrentColumn(self, gesture):
		from scriptHandler import isScriptWaiting
		if isScriptWaiting():
			return
		self._reportRowOrColumn(axis="column")

	def moveToAndReportTableElement(self, element="row", direction="next"):
		from scriptHandler import isScriptWaiting
		if isScriptWaiting():
			return
		try:
			tableID, origRow, origCol, origRowSpan, origColSpan = self._getTableCellCoords(self.selection)
			(row, col) = (origRow, 1) if element == "row" else (1, origCol)
		except LookupError:
			# Translators: The message reported when a user attempts
			# to use a table report command.
			# when the cursor is not within a table.
			import ui
			ui.message(NVDAString("Not in a table cell"))
			return
		self._tableMovementScriptHelper(movement=direction, axis=element)
		self._reportRowOrColumn(axis=element)

	@script(
		# Translators: Input help mode message for move to and report next table row
		description=_("Move to and report next table row"),
		category=SCRCAT_TABLE,
	)
	def script_moveToAndReportNextRow(self, gesture):
		self.moveToAndReportTableElement("row", "next")

	@script(
		# Translators: Input help mode message for move to and report previous table row
		description=_("Move to and report previous table row"),
		category=SCRCAT_TABLE,
	)
	def script_moveToAndReportPreviousRow(self, gesture):
		self.moveToAndReportTableElement("row", "previous")

	@script(
		# Translators: Input help mode message for move to and report next table column
		description=_("Move to and report next table column"),
		category=SCRCAT_TABLE,
	)
	def script_moveToAndReportNextColumn(self, gesture):
		self.moveToAndReportTableElement("column", "next")

	@script(
		# Translators: Input help mode message for move to and report previous table column
		description=_("Move to and report previous table column"),
		category=SCRCAT_TABLE,
	)
	def script_moveToAndReportPreviousColumn(self, gesture):
		self.moveToAndReportTableElement("column", "previous")

	def _reportCurrentCellPosition(self):
		try:
			tableID, row, col, rowSpan, colSpan = self._getTableCellCoords(self.selection)
			info = self._getTableCellAt(tableID, self.selection, row, col)
		except LookupError:
			# Translators: The message reported when a user attempts
			# to use a table report command.
			# when the cursor is not within a table.
			import ui
			ui.message(NVDAString("Not in a table cell"))
			return
		formatConfig = config.conf["documentFormatting"].copy()
		formatConfig["reportTables"] = False
		formatConfig["reportTableHeaders"] = True
		formatConfig["includeLayoutTables"] = True
		formatConfig["reportTableCellCoords"] = True
		from speech import speakTextInfo
		speakTextInfo(
			info,
			useCache=False,
			formatConfig=formatConfig,
			reason=OutputReason.QUERY, onlyInitialFields=False)

	@script(
		# Translators: Input help mode message for report current cell position command
		description=_("Report current table cell position"),
		category=SCRCAT_TABLE,
	)
	def script_reportCurrentCellPosition(self, gesture):
		from scriptHandler import isScriptWaiting
		if isScriptWaiting():
			return
		self._reportCurrentCellPosition()


# from nvda 2022.2
# nvda 2022.2 adds new table scriptsto move to first and last row/column.
# so this scripts are removed from the add-on for this nvda version  and  higher
class DocumentWithTableNavigation_2022_2(_DocumentWithTableNavigationBase):
	_myGestureMap = {
		"kb:nvda+alt+j": "reportCurrentRow",
		"kb:nvda+alt+l": "reportCurrentColumn",
	}

	def __init__(self, rootNVDAObject):
		super(DocumentWithTableNavigation_2022_2, self).__init__(rootNVDAObject)
		self.bindGestures(DocumentWithTableNavigation_2022_2._myGestureMap)
		# set category of new NVDA base table scripts to SCRCAT_TABLE
		documentBase.DocumentWithTableNavigation.script_firstRow.category = SCRCAT_TABLE
		documentBase.DocumentWithTableNavigation.script_lastRow.category = SCRCAT_TABLE
		documentBase.DocumentWithTableNavigation.script_firstColumn.category = SCRCAT_TABLE
		documentBase.DocumentWithTableNavigation.script_lastColumn.category = SCRCAT_TABLE


# until nvda 2022.1
class DocumentWithTableNavigation_2022_1(_DocumentWithTableNavigationBase):
	_myGestureMap = {
		"kb:nvda+alt+j": "reportCurrentRow",
		"kb:nvda+alt+l": "reportCurrentColumn",
		"kb:control+alt+shift+leftArrow": "moveToFirstCellOfRow",
		"kb:control+alt+shift+rightArrow": "moveToLastCellOfRow",
		"kb:control+alt+shift+upArrow": "moveToFirstCellOfColumn",
		"kb:control+alt+shift+downArrow": "moveToLastCellOfColumn",
	}

	def __init__(self, rootNVDAObject):
		super(DocumentWithTableNavigation_2022_1, self).__init__(rootNVDAObject)
		self.bindGestures(DocumentWithTableNavigation_2022_1._myGestureMap)

	@script(
		# Translators: Input help mode message for move To  First Cell Of Row
		description=_("Move to first cell of table row"),
		category=SCRCAT_TABLE,
	)
	def script_moveToFirstCellOfRow(self, gesture):
		self._tableMovementFirstOrLastScriptHelper(axis="column", movement="first")

	@script(
		# Translators: Input help mode message for move To  last Cell Of Row
		description=_("Move to last cell of table row"),
		category=SCRCAT_TABLE,
	)
	def script_moveToLastCellOfRow(self, gesture):
		self._tableMovementFirstOrLastScriptHelper(axis="column", movement="last")
	# Translators: Input help mode message for move To last cell of row command.
	# Translators: Input help mode message to move To last cell of row command.
	script_moveToLastCellOfRow.__doc__ = _("Move to last cell of table row")

	@script(
		# Translators: Input help mode message for move To  first Cell Of column
		description=_("Move to first cell of table column"),
		category=SCRCAT_TABLE,
	)
	def script_moveToFirstCellOfColumn(self, gesture):
		self._tableMovementFirstOrLastScriptHelper(axis="row", movement="first")

	@script(
		# Translators: Input help mode message for move To  last Cell Of column
		description=_("Move to last cell of table column"),
		category=SCRCAT_TABLE,
	)
	def script_moveToLastCellOfColumn(self, gesture):
		self._tableMovementFirstOrLastScriptHelper(axis="row", movement="last")
	# Translators: Input help mode message
		# for move To last cell of column command.

	def _tableMovementFirstOrLastScriptHelper(self, movement="first", axis=None):
		from speech import speakTextInfo
		import ui
		from scriptHandler import isScriptWaiting
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
				info, formatConfig=formatConfig, reason=OutputReason.CARET)
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
			info, formatConfig=formatConfig, reason=OutputReason.CARET)
		info.collapse()
		self.selection = info


# from nvda 2022.4
# this NVDA version adds scripts to read row and column
# but for now this scripts are not removed from add-on
class DocumentWithTableNavigation_2022_4(_DocumentWithTableNavigationBase):
	_myGestureMap = {
		"kb:nvda+alt+j": "reportCurrentRow",
		"kb:nvda+alt+l": "reportCurrentColumn",
	}

	def __init__(self, rootNVDAObject):
		super(DocumentWithTableNavigation_2022_4, self).__init__(rootNVDAObject)
		self.bindGestures(DocumentWithTableNavigation_2022_4._myGestureMap)
		# set category of new NVDA base table scripts to SCRCAT_TABLE
		documentBase.DocumentWithTableNavigation.script_firstRow.category = SCRCAT_TABLE
		documentBase.DocumentWithTableNavigation.script_lastRow.category = SCRCAT_TABLE
		documentBase.DocumentWithTableNavigation.script_firstColumn.category = SCRCAT_TABLE
		documentBase.DocumentWithTableNavigation.script_sayAllRow.category = SCRCAT_TABLE
		documentBase.DocumentWithTableNavigation.script_sayAllColumn.category = SCRCAT_TABLE
		documentBase.DocumentWithTableNavigation.script_lastColumn.category = SCRCAT_TABLE
		documentBase.DocumentWithTableNavigation.script_speakRow.category = SCRCAT_TABLE
		documentBase.DocumentWithTableNavigation.script_speakColumn.category = SCRCAT_TABLE

	def _reportCurrentCellPosition(self):
		try:
			cell = self._getTableCellCoords(self.selection)
			info = self._getTableCellAt(cell.tableID, self.selection, cell.row, cell.col)
		except LookupError:
			# Translators: The message reported when a user attempts
			# to use a table report command.
			# when the cursor is not within a table.
			import ui
			ui.message(NVDAString("Not in a table cell"))
			return
		formatConfig = config.conf["documentFormatting"].copy()
		formatConfig["reportTables"] = False
		formatConfig["reportTableHeaders"] = True
		formatConfig["includeLayoutTables"] = True
		formatConfig["reportTableCellCoords"] = True
		from speech import speakTextInfo
		speakTextInfo(
			info,
			useCache=False,
			formatConfig=formatConfig,
			reason=OutputReason.QUERY, onlyInitialFields=False)

	def _reportRowOrColumn(self, axis="row"):
		from speech import speakTextInfo
		try:
			oriCell = self._getTableCellCoords(self.selection)
			(row, col) = (oriCell.row, 1) if axis == "row" else (1, oriCell.col)
			info = self._getTableCellAt(oriCell.tableID, self.selection, row, col)
		except LookupError:
			# Translators: The message reported when a user attempts
			# to use a table report command.
			# when the cursor is not within a table.
			import ui
			ui.message(NVDAString("Not in a table cell"))
			return
		formatConfig = config.conf["documentFormatting"].copy()
		formatConfig["reportTables"] = True
		formatConfig["includeLayoutTables"] = True
		formatConfig["reportTableCellCoords"] = True
		while info:
			cell = self._getTableCellCoords(info)
			if axis == "row" and cell.row != oriCell.row:
				break
			elif axis == "column" and cell.col != oriCell.col:
				pass
			else:
				speakTextInfo(
					info, formatConfig=formatConfig, reason=OutputReason.MESSAGE)
			try:
				if axis == "row":
					info = self._getNearestTableCell(
						info,
						cell,
						movement="next",
						axis="column",
					)
				else:
					info = self._getNearestTableCell(
						info,
						cell,
						movement="next",
						axis="row",
					)
			except LookupError:
				break

	def moveToAndReportTableElement(self, element="row", direction="next"):
		from scriptHandler import isScriptWaiting
		if isScriptWaiting():
			return
		try:
			self._getTableCellCoords(self.selection)
		except LookupError:
			# Translators: The message reported when a user attempts
			# to use a table report command.
			# when the cursor is not within a table.
			import ui
			ui.message(NVDAString("Not in a table cell"))
			return
		self._tableMovementScriptHelper(movement=direction, axis=element)
		self._reportRowOrColumn(axis=element)
