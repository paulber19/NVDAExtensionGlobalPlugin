# globalPlugins\NVDAExtensionGlobalPlugin\computerTools\shutdown_util.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2019 - 2020 paulber19
# This file is covered by the GNU General Public License.

import addonHandler
import os
import sys
import ctypes
from ..utils.py3Compatibility import getUtilitiesPath
utilitiesPath = getUtilitiesPath()
win32Path = os.path.join(utilitiesPath, "win32")
sys.path.append(win32Path)
import win32security
import win32api
del sys.path[-1]

addonHandler.initTranslation()


def shutdown(timeout=0, forceClose=False):
	"""
	:param timeout: int , Time in second for shutdown
	:param forceClose: bool ,True for Force closing all application
	"""
	# Translators: message to user to report computer shutdown.
	rebootComputer(_("Shut down ..."), timeout, forceClose, reboot=False)


def reboot(timeout=0, forceClose=False):
	"""
	:param timeout: int , Time in second for reboot
	:param forceClose: bool ,True for Force closing applications
	"""
	# Translators: message to user to report computer rebooting.
	rebootComputer(
		_("Computer's rebooting ..."), timeout, forceClose, reboot=True)


def rebootComputer(
	message='Rebooting', timeout=30, forceClose=False, reboot=True):
	# Enable the SeShutdown privilege (which must be present in your
	# token in the first place)
	priv_flags = (win32security.TOKEN_ADJUST_PRIVILEGES | win32security.TOKEN_QUERY)
	hToken = win32security.OpenProcessToken(
		win32api.GetCurrentProcess(), priv_flags)
	priv_id = win32security.LookupPrivilegeValue(
		None, win32security.SE_SHUTDOWN_NAME)
	old_privs = win32security.AdjustTokenPrivileges(
		hToken, 0, [(priv_id, win32security.SE_PRIVILEGE_ENABLED)])
	try:
		win32api.InitiateSystemShutdown(None, message, timeout, forceClose, reboot)
	finally:
		# Restore previous privileges
		win32security.AdjustTokenPrivileges(hToken, 0, old_privs)


def suspend(hibernate=False):
	"""Puts Windows to Suspend/Sleep/Standby or Hibernate.
	Parameters
	hibernate: bool, default False
		If False (default), system will enter Suspend/Sleep/Standby state.
		If True, system will Hibernate, but only if Hibernate is enabled in the
		system settings. If it's not, system will Sleep.
	"""
	# Enable the SeShutdown privilege (which must be present in your
	# token in the first place)
	priv_flags = (
		win32security.TOKEN_ADJUST_PRIVILEGES | win32security.TOKEN_QUERY)
	hToken = win32security.OpenProcessToken(
		win32api.GetCurrentProcess(), priv_flags)
	priv_id = win32security.LookupPrivilegeValue(
		None, win32security.SE_SHUTDOWN_NAME)
	old_privs = win32security.AdjustTokenPrivileges(
		hToken, 0, [(priv_id, win32security.SE_PRIVILEGE_ENABLED)])
	if (not win32api.GetPwrCapabilities()['HiberFilePresent'] and hibernate):
		import warnings
		# Translators: message to user to report hibernate mode is not available.
		warnings.warn(_("Hibernate isn't available. So, sleep mode is activated."))
	try:
		ctypes.windll.powrprof.SetSuspendState(not hibernate, True, False)
	except Exception:
		# True=> Standby; False=> Hibernate
		# https://msdn.microsoft.com/pt-br/library/windows/desktop/aa373206(v=vs.85).aspx
		# says the second parameter has no effect.
		win32api.SetSystemPowerState(not hibernate, True)
	# Restore previous privileges
	win32security.AdjustTokenPrivileges(hToken, 0, old_privs)
