# NVDAExtensionGlobalPlugin/utils/secure.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2022  paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

import globalVars


def inSecureMode():
	return globalVars.appArgs.secure
