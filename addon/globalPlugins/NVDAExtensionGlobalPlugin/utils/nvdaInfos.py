# globalPlugins\NVDAExtensionGlobalPlugin/utils/nvdaInfos.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2025  paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.

try:
	# for nvda versions < 2026.1
	from versionInfo import version_year, version_major
except ImportError:
	# for NVDA versions >= 2026.1
	from buildVersion import version_year, version_major

NVDAVersion = [version_year, version_major]
