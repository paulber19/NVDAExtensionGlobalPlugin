#NVDAExtensionGlobalPlugin/__init__.py
# a part of NVDAExtensionGlobalPlugin add-on
#Copyright (C) 2016-2017 Paulber19
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.
import globalVars
import config

#this add-on is disabled when loading in the secure screen,
# as well as if NVDA is running as a Windows Store Desktop Bridge application.
if (globalVars.appArgs.secure 
	or (hasattr (config, "isAppX") and config.isAppX)):
	import globalPluginHandler
	class GlobalPlugin (globalPluginHandler.GlobalPlugin):
		pass
else:

	from . import theGlobalPlugin
	class GlobalPlugin (theGlobalPlugin.NVDAExtensionGlobalPlugin):
		def chooseNVDAObjectOverlayClasses(self, obj, clsList):
			super(GlobalPlugin , self).chooseNVDAObjectOverlayClasses(obj, clsList)