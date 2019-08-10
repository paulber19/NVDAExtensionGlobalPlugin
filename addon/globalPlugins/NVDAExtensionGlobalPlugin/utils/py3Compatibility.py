#NVDAExtensionGlobalPlugin/utils/py3Compatibility.py
# a part of NVDAExtensionGlobalPlugin add-on
# Copyright 2019 paulber19
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.


import addonHandler
import os
from logHandler import log
import sys
py3 = sys.version.startswith("3")
# Python 3 preparation (a compatibility layer until Six module is included).
if py3:
	rangeGen = range 
	baseString = str  
	uniCHR = chr
	_unicode= str
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
def importStringIO ():
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

def getUtilitiesPath():
	curAddon = addonHandler.getCodeAddon()
	if py3:
		return os.path.join(curAddon.path, "utilitiesPy3")
	else:
		return os.path.join(curAddon.path, "utilities")	
