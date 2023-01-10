# globalPlugins\NVDAExtensionGlobalPlugin\clipboardCommandAnnouncement\clipboard.py
# a part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2022 Paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

# some parts of code were inspired from the code   of Clipboard_monitor.py module of clipSpeak add-on
# written By Damien Lindley, created: 20th April 2017

from winUser import user32
from logHandler import log


class ClipboardManager(object):

	def __init__(self):
		log.debug("Initialising clipboard manager.")
		self.sequenceNumber = user32.GetClipboardSequenceNumber()
		log.debug("clipboard manager init: current sequence number = %s" % self.sequenceNumber)

	def getClipboardDatas(self):
		log.debug("getting clipboard data...")
		data = {}
		log.debug("Opening the clipboard for enumeration.")
		try:
			user32.OpenClipboard(None)
		except Exception:
			log.debug("Clipboard failed to open. Cannot enumerate.")
			return data
		format = 0
		while True:
			try:
				format = user32.EnumClipboardFormats(format)
				log.debug("Retrieving clipboard format: %d" % format)
				if format == 0:
					break
				pos = str(format)
				log.debug("Retrieving data for format %s" % pos)
				data[pos] = user32.GetClipboardData(format)
				log.debug("Data retrieved: %r" % data[pos])
			except Exception:
				log.debug("Cannot retrieve data.")
				break
		log.debug("Closing clipboard.")
		user32.CloseClipboard()
		return data

	def changed(self):
		log.debug("Checking for clipboard changes.")
		sequenceNumber = user32.GetClipboardSequenceNumber()
		if sequenceNumber == self.sequenceNumber:
			log.debug("No changes detected.")
			return False
		log.debug("Clipboard data has changed. Updating sequence number: %s" % sequenceNumber)
		self.sequenceNumber = sequenceNumber
		return True

	@property
	def isEmpty(self):
		log.debug("check if clipboard is empty")
		log.debug("Opening the clipboard for enumeration.")
		try:
			user32.OpenClipboard(None)
		except Exception:
			log.debug("Clipboard failed to open. Cannot check")
			return False
		format = 0
		try:
			format = user32.EnumClipboardFormats(format)
		except Exception:
			log.debug("Cannot enumerate.")
			format = 1
		log.debug("Closing clipboard.")
		user32.CloseClipboard()
		return format == 0

	def clear(self):
		log.debug("Opening the clipboard for clearing.")
		try:
			user32.OpenClipboard(None)
		except Exception:
			log.debug("Clipboard failed to open. Cannot clear.")
			return False
		res = user32.EmptyClipboard()
		if not res:
			log.debug("Clipboard failed to clear. Cannot clear.")
		user32.CloseClipboard()
		log.debug("clipboard is cleared")
		return res
