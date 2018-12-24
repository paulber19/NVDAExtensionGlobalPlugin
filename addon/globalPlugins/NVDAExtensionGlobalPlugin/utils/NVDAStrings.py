#A part of NonVisual Desktop Access (NVDA)
#Copyright (C) 2008-2016 NV Access Limited, Dinesh Kaushal, Davy Kager
#This file is covered by the GNU General Public License.
#See the file COPYING for more details.

def NVDAString(s):
	""" A simple function to bypass the addon translation system,
	so it can take advantage from the NVDA translations directly.
	Based on implementation made by Alberto Buffolino
	https://github.com/nvaccess/nvda/issues/4652 """
	
	return _(s)

