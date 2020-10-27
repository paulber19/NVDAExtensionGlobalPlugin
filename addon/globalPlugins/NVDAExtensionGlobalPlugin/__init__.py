# globalPlugins\NVDAExtensionGlobalPlugin\__init__.py
# a part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2016 - 2020 Paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

from . import theGlobalPlugin

class GlobalPlugin (theGlobalPlugin.NVDAExtensionGlobalPlugin):
	# ??? this definition is necessary.
	# if not, the method of the NVDAExtensionGlobalPlugin class is never called.
	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		super(GlobalPlugin, self).chooseNVDAObjectOverlayClasses(obj, clsList)
