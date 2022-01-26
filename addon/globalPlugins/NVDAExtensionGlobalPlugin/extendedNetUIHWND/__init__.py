# globalPlugins\NVDAExtensionGlobalPlugin\ComplexSymbols\__init__
# A part of NvDAextensionGlobalPlugin
# Copyright (C) 2016 - 2022 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import NVDAObjects
import config


class ExtendedNetUIHWND (NVDAObjects.NVDAObject):
	def event_focusEntered(self):
		oldPresentationReportObjectDescriptions = config.conf["presentation"]["reportObjectDescriptions"]
		config.conf["presentation"]["reportObjectDescriptions"] = False
		super(ExtendedNetUIHWND, self).event_focusEntered()
		config.conf["presentation"]["reportObjectDescriptions"] = oldPresentationReportObjectDescriptions

	def event_gainFocus(self):
		oldPresentationReportObjectDescriptions = config.conf["presentation"]["reportObjectDescriptions"]
		config.conf["presentation"]["reportObjectDescriptions"] = False
		super(ExtendedNetUIHWND, self).event_gainFocus()
		config.conf["presentation"]["reportObjectDescriptions"] = oldPresentationReportObjectDescriptions


def chooseNVDAObjectOverlayClasses(obj, clsList):
	if obj.windowClassName == "NetUIHWND":
		clsList.insert(0, ExtendedNetUIHWND)
