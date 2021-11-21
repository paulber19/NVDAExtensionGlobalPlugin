# globalPlugins\NVDAExtensionGlobalPlugin\utils\NVDAStrings.py
# Copyright (C) 2017 - 2020 Paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.


def NVDAString(s):
	""" A simple function to bypass the addon translation system,
	so it can take advantage from the NVDA translations directly.
	Based on implementation made by Alberto Buffolino
	https://github.com/nvaccess/nvda/issues/4652 """
	return _(s)


def NVDAString_pgettext(c, s):
	return pgettext(c, s)
