# globalPlugins\NVDAExtensionGlobalPlugin\browseModeEx\NVDAObjectsIAccessible.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2016 - 2023 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

from logHandler import log
import config
import controlTypes
import NVDAObjects
from .virtualBuffersEx import MSHTMLEx, Gecko_ia2_Ex, ChromeVBufEx
import NVDAObjects.IAccessible.chromium


class NVDAObjectMSHTMLEx(NVDAObjects.IAccessible.MSHTML.MSHTML):
	def _get_treeInterceptorClass(self):
		if (
			self.role in (controlTypes.Role.DOCUMENT, controlTypes.Role.APPLICATION, controlTypes.Role.DIALOG)
			and not self.isContentEditable):
			return MSHTMLEx
		return super(NVDAObjectMSHTMLEx, self).treeInterceptorClass


class NVDAObjectMozillaDocumentEx(NVDAObjects.IAccessible.mozilla .Document):
	def _get_treeInterceptorClass(self):
		if controlTypes.State.EDITABLE not in self.states:
			return Gecko_ia2_Ex
		return super(NVDAObjectMozillaDocumentEx, self).treeInterceptorClass


class ChromiumDocument(NVDAObjects.IAccessible.chromium.Document):
	def _get_treeInterceptorClass(self):
		shouldLoadVBufOnBusyFeatureFlag = bool(
			config.conf["virtualBuffers"]["loadChromiumVBufOnBusyState"]
		)
		vBufUnavailableStates = {  # if any of these are in states, don't return ChromeVBuf
			controlTypes.State.EDITABLE,
		}
		if not shouldLoadVBufOnBusyFeatureFlag:
			log.debug(
				f"loadChromiumVBufOnBusyState feature flag is {shouldLoadVBufOnBusyFeatureFlag},"
				" vBuf WILL NOT be loaded when state of the document is busy."
			)
			vBufUnavailableStates.add(controlTypes.State.BUSY)
		else:
			log.debug(
				f"loadChromiumVBufOnBusyState feature flag is {shouldLoadVBufOnBusyFeatureFlag},"
				" vBuf WILL be loaded when state of the document is busy."
			)
		if self.states.intersection(vBufUnavailableStates):
			return super().treeInterceptorClass
		return ChromeVBufEx
