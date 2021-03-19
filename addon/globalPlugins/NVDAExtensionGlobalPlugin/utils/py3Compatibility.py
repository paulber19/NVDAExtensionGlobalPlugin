# globalPlugins\NVDAExtensionGlobalPlugin\utils\py3Compatibility.py
# a part of NVDAExtensionGlobalPlugin add-on
# Copyright 2019 - 2020 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import addonHandler
import os
import sys
py3 = sys.version.startswith("3")
# Python 3 preparation (a compatibility layer until Six module is included).
if py3:
	rangeGen = range
	baseString = str
	uniCHR = chr
	_unicode = str
else:
	rangeGen = xrange
	baseString = basestring
	uniCHR = unichr
	_unicode = unicode


def iterate_items(to_iterate):
	if py3:
		return to_iterate.items()
	else:
		return to_iterate.iteritems()


def importStringIO():
	if py3:
		from io import StringIO
	else:
		from cStringIO import StringIO
	return StringIO


def longint(i):
	if py3:
		return i
	else:
		return long(i)


def reLoad(mod):
	if py3:
		import importlib
		importlib.reload(mod)
	else:
		reload(mod)


def getCommonUtilitiesPath():
	curAddonPath = getAddonPath()
	return os.path.join(curAddonPath, "utilities")


def getUtilitiesPath():
	curAddonPath = getAddonPath()
	if py3:
		if sys.version .startswith("3.8"):
			utilities = "utilitiesPy38"
		else:
			utilities = "utilitiesPy3"
	else:
		utilities = "utilitiesPy2"
	return os.path.join(curAddonPath, utilities)


def getAddonPath(addon=None):
	if addon is None:
		addon = addonHandler.getCodeAddon()
	if sys.version.startswith("3"):
		# for python 3
		addonPath = addon.path
	else:
		# for python 2
		addonPath = addon.path.encode("mbcs")
	return addonPath
