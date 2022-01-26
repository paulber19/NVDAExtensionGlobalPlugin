# -*- coding: UTF-8 -*-
# guiHelper.py
# A part of NonVisual Desktop Access (NVDA)
# Copyright (C) 2016 NV Access Limited
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# only the changes between nvda 2020.4 and 2021.1
# necessary to maintain compatibility with 2020.4 and lower


import wx
from gui.guiHelper import BoxSizerHelper, LabeledControlHelper, ButtonHelper


class BoxSizerHelper(BoxSizerHelper):

	def addLabeledControl(self, labelText, wxCtrlClass, **kwargs):
		""" Convenience method to create a labeled control
			@param labelText: Text to use when constructing the wx.StaticText to label the control.
			@type LabelText: String
			@param wxCtrlClass: Control class to construct and associate with the label
			@type wxCtrlClass: Some wx control type EG wx.TextCtrl
			@param kwargs: keyword arguments used to construct the wxCtrlClass.
			As taken by guiHelper.LabeledControlHelper

			Relies on guiHelper.LabeledControlHelper and thus guiHelper.associateElements, and therefore inherits any
			limitations from there.
		"""
		parent = self._parent
		if isinstance(self.sizer, wx.StaticBoxSizer):
			parent = self.sizer.GetStaticBox()
		labeledControl = LabeledControlHelper(parent, labelText, wxCtrlClass, **kwargs)
		if(isinstance(labeledControl.control, (wx.ListCtrl, wx.ListBox, wx.TreeCtrl))):
			self.addItem(labeledControl.sizer, flag=wx.EXPAND, proportion=1)
		else:
			self.addItem(labeledControl.sizer)
		return labeledControl.control

	def addDialogDismissButtons(self, buttons, separated=False):
		""" Adds and aligns the buttons for dismissing the dialog; e.g. "ok | cancel". These buttons are expected
		to be the last items added to the dialog.
		Buttons that launch an action, do not dismiss the dialog, or are not
		the last item should be added via L{addItem}
		@param buttons: The buttons to add
		@type buttons:
			wx.Sizer or guiHelper.ButtonHelper or single wx.Button
			or a bit list of the following flags: wx.OK, wx.CANCEL, wx.YES, wx.NO, wx.APPLY, wx.CLOSE,
			wx.HELP, wx.NO_DEFAULT
		@param separated:
			Whether a separator should be added between the dialog content and its footer.
			Should be set to L{False} for message or single input dialogs, L{True} otherwise.
		@type separated: L{bool}
		"""
		parent = self._parent
		if isinstance(self.sizer, wx.StaticBoxSizer):
			parent = self.sizer.GetStaticBox()
		if self.sizer.GetOrientation() != wx.VERTICAL:
			raise NotImplementedError(
				"Adding dialog dismiss buttons to a horizontal BoxSizerHelper is not implemented."
			)
		if isinstance(buttons, ButtonHelper):
			toAdd = buttons.sizer
		elif isinstance(buttons, (wx.Sizer, wx.Button)):
			toAdd = buttons
		elif isinstance(buttons, int):
			toAdd = parent.CreateButtonSizer(buttons)
		else:
			raise NotImplementedError("Unknown type: {}".format(buttons))
		if separated:
			self.addItem(wx.StaticLine(parent), flag=wx.EXPAND)
		self.addItem(toAdd, flag=wx.ALIGN_RIGHT)
		self.dialogDismissButtonsAdded = True
		return buttons
