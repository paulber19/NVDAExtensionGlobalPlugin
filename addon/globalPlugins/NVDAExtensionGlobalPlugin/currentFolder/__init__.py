# globalPlugins\NVDAExtensionGlobalPlugin\currentFolder\__init__
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2016 - 2020 Daniel Poiraud , Paulber19
# This file is covered by the GNU General Public License.

import addonHandler
import api
import ui

addonHandler.initTranslation()


def findChildObjectByClassName(obj, className):
	for o in obj.children:
		if o.windowClassName == className:
			return o
	return None


def getCurrentFolder():
	oForeground = api.getForegroundObject()
	# for Office 2003 and dialogbox based on XP
	windowText = oForeground.windowText
	# Translators: this is title of classic Window to manage file.
	if windowText in [_("Open"), _("Save"), _("Save as"), _("Find in")]:
		if 'bosa_sdm_' in oForeground.windowClassName:
			oCurrentFolder = oForeground.children[14]
			path = oCurrentFolder.name
			folder = oCurrentFolder.value
			return (path, folder)
		elif '#32770' in oForeground.windowClassName:
			if oForeground.children[1].windowClassName == 'ComboBox':
				oCurrentFolder = oForeground.children[1]
				path = "%s\\%s" % (oCurrentFolder.name, oCurrentFolder.value)
				path = oCurrentFolder.name
				folder = oCurrentFolder.value
				return (path, folder)
	classNames = (
		"WorkerW",
		"ReBarWindow32",
		"Address Band Root",
		"msctls_progress32",
		"Breadcrumb Parent",
		"ToolbarWindow32")
	o = oForeground
	for className in classNames:
		o = findChildObjectByClassName(o, className)
		if o is None:
			break
	if o is None:
		return None
	pathList = []
	for o in o.children:
		pathList.append(o.name)
	path = "\\".join(pathList[:-1])
	folder = pathList[-1]
	return (path, folder)


def reportCurrentFolder(sayPath=False):
	# Translators: message to the user.
	msgFolderNotFound = _("Selected folder name not found")
	currentFolder = getCurrentFolder()
	if currentFolder is None:
		ui.message(msgFolderNotFound)
		return
	(path, folder) = currentFolder
	if not sayPath:
		# report folder name
		ui.message(_("Folder %s") % folder)
	else:
		# report full folder path
		ui.message("%s\\%s" % (path, folder))
