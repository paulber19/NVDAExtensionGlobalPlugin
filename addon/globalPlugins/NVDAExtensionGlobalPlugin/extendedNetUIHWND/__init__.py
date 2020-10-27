# globalPlugins\NVDAExtensionGlobalPlugin\ComplexSymbols\__init__
# A part of NvDAextensionGlobalPlugin
# Copyright (C) 2016 - 2020 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import NVDAObjects
import config


class ExtendedNetUIHWND (NVDAObjects.NVDAObject):
	def event_focusEntered(self):
		oldPresentationReportObjectDescriptions = config.conf["presentation"]["reportObjectDescriptions"]  # noqa:E501
		config.conf["presentation"]["reportObjectDescriptions"] = False
		super(ExtendedNetUIHWND, self).event_focusEntered()
		config.conf["presentation"]["reportObjectDescriptions"] = oldPresentationReportObjectDescriptions  # noqa:E501

	def event_gainFocus(self):
		oldPresentationReportObjectDescriptions = config.conf["presentation"]["reportObjectDescriptions"]  # noqa:E501
		config.conf["presentation"]["reportObjectDescriptions"] = False
		super(ExtendedNetUIHWND, self).event_gainFocus()
		config.conf["presentation"]["reportObjectDescriptions"] = oldPresentationReportObjectDescriptions  # noqa:E501


def chooseNVDAObjectOverlayClasses(obj, clsList):
	if obj.windowClassName == "NetUIHWND":
		clsList.insert(0, ExtendedNetUIHWND)
