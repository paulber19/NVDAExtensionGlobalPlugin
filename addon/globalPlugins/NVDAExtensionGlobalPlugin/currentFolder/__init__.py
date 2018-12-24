#NVDAExtensionGlobalPlugin/ComplexSymbols/__init__
#A part of NVDAExtensionGlobalPlugin
#Copyright (C) 2016  Daniel Poiraud , Paulber19
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.

import addonHandler
addonHandler.initTranslation()

import sys
import api
import ui


def reportCurrentFolder (sayPath = False):

	# Translators:  message to the user.
	msgFolderNotFound = _("Selected folder name not found")
	
	def findChildObjectByClassName(obj, className):
		for o in obj.children:
			if o.windowClassName == className:
				return o
		
		return None
	oForeground = api.getForegroundObject()
	# for Office 2003 and dialogbox based on XP
	# Translators: this is title of classic Window to manage file.
	if oForeground.windowText in [_("Open"),_("Save"), _("Save as"), _("Find in")] :
		if 'bosa_sdm_' in oForeground.windowClassName:
			oCurrentFolder= oForeground.children[14]
			ui.message("%s %s" %(oCurrentFolder.name, oCurrentFolder.value))
			return
		elif '#32770' in oForeground.windowClassName:
			if oForeground.children[1].windowClassName == 'ComboBox':
				oCurrentFolder= oForeground.children[1]
				ui.message("%s %s" %(oCurrentFolder.name, oCurrentFolder.value))
				return
	
	classNamePath = ("WorkerW", "ReBarWindow32", "Address Band Root", "msctls_progress32", "Breadcrumb Parent", "ToolbarWindow32")
	o= oForeground
	for className in classNamePath:
		o = findChildObjectByClassName(o, className)
		if o is None:
			break
	
	if o is None:
		ui.message(msgFolderNotFound)
		return
	
	oToolbarWindow32 = o
	count = oToolbarWindow32.childCount

	if not sayPath:
		# report folder name
		ui.message (_("Folder %s")%o.children[-1].name)
	else:
		#report full folder path
		text = ""
		for o in o.children:
			text = text + " %s\\" %o.name
		ui.message (text[:-1])  
	return
	