# globalPlugins/NVDAextensionGlobalPlugin\gui\messageBoxPatches.py
# a part of NVDAExtensionGlobalPlugin add-on
# Copyright 2025 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
from logHandler import log
import gui
import gui.message
import config

_NVDAGuiMessageBox = None
_NVDAGuiMessageMessageBox = None


# NVDA messageBox method patched to say in all cases the window content.
# even if the user has chosen not to have NVDA announce the description of the object

_reportObjectDescriptionOptions = []
_NVDAMessageDialogShowModal = None


def myMessageDialogFunc(func, *args, **kwargs):
	log.debug("myMessageDialogInit")
	c = config.conf
	pre = c["presentation"]["reportObjectDescriptions"]
	_reportObjectDescriptionOptions.append((c, pre))
	c["presentation"]["reportObjectDescriptions"] = True
	res = func(*args, **kwargs)
	(c, pre) = _reportObjectDescriptionOptions.pop()
	c["presentation"]["reportObjectDescriptions"] = pre
	return res


def myMessageBox(*args, **kwargs):
	return myMessageDialogFunc(_NVDAGuiMessageMessageBox, *args, **kwargs)


def myMessageDialogShowModal(*args, **kwargs):
	return myMessageDialogFunc(_NVDAMessageDialogShowModal, *args, **kwargs)


def initialize():
	global _NVDAGuiMessageBox, _NVDAGuiMessageMessageBox
	# replace nvda gui.messageBox and NVDA gui.message.messageBox by myMessageBox
	_NVDAGuiMessageBox = gui.messageBox
	_NVDAGuiMessageMessageBox = gui.message.messageBox
	gui.messageBox = myMessageBox
	gui.message.messageBox = myMessageBox
	log.debug(
		"gui.messageBox and gui.message.messageBox patched by: %s of %s module "
		% (myMessageBox.__name__, myMessageBox.__module__))
	global _NVDAMessageDialogShowModal
	from gui.message import MessageDialog
	_NVDAMessageDialogShowModal = MessageDialog.ShowModal
	MessageDialog.ShowModal = myMessageDialogShowModal
	log.debug(
		"gui.message.MessageDialog.ShowModal patched by: %s of %s module "
		% (myMessageDialogShowModal.__name__, myMessageDialogShowModal.__module__))


def terminate():
	global _NVDAGuiMessageBox, _NVDAGuiMessageMessageBox
	# restore NVDA gui.messageBox and gui.message.messageBox
	if _NVDAGuiMessageMessageBox is not None:
		gui.messageBox = _NVDAGuiMessageBox
		_NVDAGuiMessageBox = None
		gui.message.messageBox = _NVDAGuiMessageMessageBox
		_NVDAGuiMessageMessageBox = None
	global _NVDAMessageDialogShowModal
	if _NVDAMessageDialogShowModal is not None:
		from gui.message import MessageDialog
		MessageDialog.ShowModal = _NVDAMessageDialogShowModal
		_NVDAMessageDialogShowModal = None
