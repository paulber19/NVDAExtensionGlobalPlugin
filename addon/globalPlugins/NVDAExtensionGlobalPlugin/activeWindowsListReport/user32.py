# globalPlugins\NVDAExtensionGlobalPlugin\activeWindowsListReport\user32.py
# A part of NVDAExtensionGlobalPlugin add-on
# Copyright (C) 2019 - 2020 paulber19
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# this module is based on some part of The WinAppDbg python module
# (author :Mario Vilas)
# Homepage = https://github.com/MarioVilas/winappdbg/


import winUser
import ctypes
import ctypes.wintypes
from ctypes.wintypes import HWND, LPPOINT
# win32con constant
WS_EX_APPWINDOW = 262144
WS_EX_TOOLWINDOW = 128
WS_EX_NOACTIVATE = 0x08000000
WS_EX_NOREDIRECTIONBITMAP = 0x00200000
SW_MAXIMIZE = 3

# flags placement
WPF_RESTORETOMAXIMIZED = 0x0002
SW_SHOWNORMAL = 1
SW_SHOWMINIMIZED = 2
SW_SHOWMAXIMIZED = 3

# ctypes constants
NULL = None
BOOL = ctypes.c_int32
DWORD = ctypes.c_uint32
HANDLE = ctypes.c_void_p
byref = ctypes.byref
sizeof = ctypes.sizeof
LPVOID = ctypes.c_void_p
PVOID = LPVOID
LPARAM = LPVOID
WINFUNCTYPE = ctypes.WINFUNCTYPE
WNDENUMPROC = WINFUNCTYPE(BOOL, HANDLE, PVOID)
UINT = ctypes.c_uint32
LONG = ctypes.c_int32
POINTER = ctypes.POINTER
HWND_DESKTOP = 0
ERROR_SUCCESS = 0
ERROR_NO_MORE_FILES = 18


class RECT(ctypes.Structure):
	_fields_ = [
		('left', LONG),
		('top', LONG),
		('right', LONG),
		('bottom', LONG),
	]


PRECT = POINTER(RECT)
LPRECT = PRECT


class POINT(ctypes.Structure):
	_fields_ = [
		('x', LONG),
		('y', LONG),
	]


class Point(object):
	"""
	Python wrapper over the L{POINT} class.

	@type x: int
	@ivar x: Horizontal coordinate
	@type y: int
	@ivar y: Vertical coordinate
	"""

	def __init__(self, x=0, y=0):
		"""
		@see: L{POINT}
		@type x: int
		@param x: Horizontal coordinate
		@type y: int
		@param y: Vertical coordinate
		"""
		self.x = x
		self.y = y

	def __iter__(self):
		return (self.x, self.y).__iter__()

	def __len__(self):
		return 2

	def __getitem__(self, index):
		return (self.x, self.y)[index]

	def __setitem__(self, index, value):
		if index == 0:
			self.x = value
		elif index == 1:
			self.y = value
		else:
			raise IndexError("index out of range")

	@property
	def _as_parameter_(self):
		"""
		Compatibility with ctypes.
		Allows passing transparently a Point object to an API call.
		"""
		return POINT(self.x, self.y)

	def screen_to_client(self, hWnd):
		"""
		Translates window screen coordinates to client coordinates.

		@see: L{client_to_screen}, L{translate}

		@type hWnd: int or L{HWND} or L{system.Window}
		@param hWnd: Window handle.

		@rtype: L{Point}
		@return: New object containing the translated coordinates.
		"""
		return winUser.ScreenToClient(hWnd, self)

	def client_to_screen(self, hWnd):
		"""
		Translates window client coordinates to screen coordinates.

		@see: L{screen_to_client}, L{translate}

		@type hWnd: int or L{HWND} or L{system.Window}
		@param hWnd: Window handle.

		@rtype: L{Point}
		@return: New object containing the translated coordinates.
		"""
		return winUser.ClientToScreen(hWnd, self)

	def translate(self, hWndFrom=HWND_DESKTOP, hWndTo=HWND_DESKTOP):
		"""
		Translate coordinates from one window to another.

		@note: To translate multiple points it's more efficient to use the
			L{MapWindowPoints} function instead.

		@see: L{client_to_screen}, L{screen_to_client}

		@type hWndFrom: int or L{HWND} or L{system.Window}
		@param hWndFrom: Window handle to translate from.
			Use C{HWND_DESKTOP} for screen coordinates.

		@type hWndTo: int or L{HWND} or L{system.Window}
		@param hWndTo: Window handle to translate to.
			Use C{HWND_DESKTOP} for screen coordinates.

		@rtype: L{Point}
		@return: New object containing the translated coordinates.
		"""
		return MapWindowPoints(hWndFrom, hWndTo, [self])


class Rect(object):
	"""
	Python wrapper over the L{RECT} class.

	@type left: int
	@ivar left: Horizontal coordinate for the top left corner.
	@type top: int
	@ivar top: Vertical coordinate for the top left corner.
	@type right: int
	@ivar right: Horizontal coordinate for the bottom right corner.
	@type bottom: int
	@ivar bottom: Vertical coordinate for the bottom right corner.

	@type width: int
	@ivar width: Width in pixels. Same as C{right - left}.
	@type height: int
	@ivar height: Height in pixels. Same as C{bottom - top}.
	"""

	def __init__(self, left=0, top=0, right=0, bottom=0):
		"""
		@see: L{RECT}
		@type left: int
		@param left: Horizontal coordinate for the top left corner.
		@type top: int
		@param top: Vertical coordinate for the top left corner.
		@type right: int
		@param right: Horizontal coordinate for the bottom right corner.
		@type bottom: int
		@param bottom: Vertical coordinate for the bottom right corner.
		"""
		self.left = left
		self.top = top
		self.right = right
		self.bottom = bottom

	def __iter__(self):
		return (self.left, self.top, self.right, self.bottom).__iter__()

	def __len__(self):
		return 2

	def __getitem__(self, index):
		return (self.left, self.top, self.right, self.bottom)[index]

	def __setitem__(self, index, value):
		if index == 0:
			self.left = value
		elif index == 1:
			self.top = value
		elif index == 2:
			self.right = value
		elif index == 3:
			self.bottom = value
		else:
			raise IndexError("index out of range")

	@property
	def _as_parameter_(self):
		"""
		Compatibility with ctypes.
		Allows passing transparently a Point object to an API call.
		"""
		return RECT(self.left, self.top, self.right, self.bottom)

	def __get_width(self):
		return self.right - self.left

	def __get_height(self):
		return self.bottom - self.top

	def __set_width(self, value):
		self.right = value - self.left

	def __set_height(self, value):
		self.bottom = value - self.top

	width = property(__get_width, __set_width)
	height = property(__get_height, __set_height)

	def screen_to_client(self, hWnd):
		"""
		Translates window screen coordinates to client coordinates.

		@see: L{client_to_screen}, L{translate}

		@type hWnd: int or L{HWND} or L{system.Window}
		@param hWnd: Window handle.

		@rtype: L{Rect}
		@return: New object containing the translated coordinates.
		"""
		topleft = winUser.ScreenToClient(hWnd, (self.left, self.top))
		bottomright = winUser.ScreenToClient(hWnd, (self.bottom, self.right))
		return Rect(topleft.x, topleft.y, bottomright.x, bottomright.y)

	def client_to_screen(self, hWnd):
		"""
		Translates window client coordinates to screen coordinates.

		@see: L{screen_to_client}, L{translate}

		@type hWnd: int or L{HWND} or L{system.Window}
		@param hWnd: Window handle.

		@rtype: L{Rect}
		@return: New object containing the translated coordinates.
		"""
		topleft = winUser.ClientToScreen(hWnd, (self.left, self.top))
		bottomright = winUser.ClientToScreen(hWnd, (self.bottom, self.right))
		return Rect(topleft.x, topleft.y, bottomright.x, bottomright.y)

	def translate(self, hWndFrom=HWND_DESKTOP, hWndTo=HWND_DESKTOP):
		"""
		Translate coordinates from one window to another.

		@see: L{client_to_screen}, L{screen_to_client}

		@type hWndFrom: int or L{HWND} or L{system.Window}
		@param hWndFrom: Window handle to translate from.
			Use C{HWND_DESKTOP} for screen coordinates.

		@type hWndTo: int or L{HWND} or L{system.Window}
		@param hWndTo: Window handle to translate to.
			Use C{HWND_DESKTOP} for screen coordinates.

		@rtype: L{Rect}
		@return: New object containing the translated coordinates.
		"""
		points = [(self.left, self.top), (self.right, self.bottom)]
		return MapWindowPoints(hWndFrom, hWndTo, points)


kernel32 = ctypes.windll.kernel32


def MapWindowPoints(hWndFrom, hWndTo, lpPoints):
	_MapWindowPoints = ctypes.windll.user32.MapWindowPoints
	_MapWindowPoints.argtypes = [HWND, HWND, LPPOINT, UINT]
	_MapWindowPoints.restype = ctypes.c_int
	cPoints = len(lpPoints)
	lpPoints = (Point * cPoints)(* lpPoints)
	kernel32.SetLastError(ERROR_SUCCESS)
	number = _MapWindowPoints(hWndFrom, hWndTo, byref(lpPoints), cPoints)
	if number == 0:
		errcode = kernel32.GetLastError()
		if errcode != ERROR_SUCCESS:
			raise ctypes.WinError(errcode)
	x_delta = number & 0xFFFF
	y_delta = (number >> 16) & 0xFFFF
	return x_delta, y_delta, [(Point.x, Point.y) for Point in lpPoints]


class WindowPlacement(object):
	"""
	Python wrapper over the L{WINDOWPLACEMENT} class.
	"""

	def __init__(self, wp=None):
		"""
		@type wp: L{WindowPlacement} or L{WINDOWPLACEMENT}
		@param wp: Another window placement object.
		"""

		# Initialize all properties with empty values.
		self.flags = 0
		self.showCmd = 0
		self.ptMinPosition = Point()
		self.ptMaxPosition = Point()
		self.rcNormalPosition = Rect()

		# If a window placement was given copy it's properties.
		if wp:
			self.flags = wp.flags
			self.showCmd = wp.showCmd
			self.ptMinPosition = Point(wp.ptMinPosition.x, wp.ptMinPosition.y)
			self.ptMaxPosition = Point(wp.ptMaxPosition.x, wp.ptMaxPosition.y)
			self.rcNormalPosition = Rect(
				wp.rcNormalPosition.left,
				wp.rcNormalPosition.top,
				wp.rcNormalPosition.right,
				wp.rcNormalPosition.bottom,
			)

	@property
	def _as_parameter_(self):
		"""
		Compatibility with ctypes.
		Allows passing transparently a Point object to an API call.
		"""
		wp = WINDOWPLACEMENT()
		wp.length = sizeof(wp)
		wp.flags = self.flags
		wp.showCmd = self.showCmd
		wp.ptMinPosition.x = self.ptMinPosition.x
		wp.ptMinPosition.y = self.ptMinPosition.y
		wp.ptMaxPosition.x = self.ptMaxPosition.x
		wp.ptMaxPosition.y = self.ptMaxPosition.y
		wp.rcNormalPosition.left = self.rcNormalPosition.left
		wp.rcNormalPosition.top = self.rcNormalPosition.top
		wp.rcNormalPosition.right = self.rcNormalPosition.right
		wp.rcNormalPosition.bottom = self.rcNormalPosition.bottom
		return wp


class WINDOWPLACEMENT(ctypes.Structure):
	_fields_ = [
		('length', UINT),
		('flags', UINT),
		('showCmd', UINT),
		('ptMinPosition', POINT),
		('ptMaxPosition', POINT),
		('rcNormalPosition', RECT),
	]


PWINDOWPLACEMENT = POINTER(WINDOWPLACEMENT)
LPWINDOWPLACEMENT = PWINDOWPLACEMENT


def RaiseIfZero(result, func=None, arguments=()):
	"""
	Error checking for most Win32 API calls.

	The function is assumed to return an integer, which is C{0} on error.
	In that case the C{WindowsError} exception is raised.
	"""
	if not result:
		raise ctypes.WinError()
	return result


def getWindowPlacement(hWnd):
	_GetWindowPlacement = ctypes.windll.user32.GetWindowPlacement
	_GetWindowPlacement.argtypes = [HANDLE, PWINDOWPLACEMENT]
	_GetWindowPlacement.restype = bool
	_GetWindowPlacement.errcheck = RaiseIfZero
	lpwndpl = WINDOWPLACEMENT()
	lpwndpl.length = sizeof(lpwndpl)
	_GetWindowPlacement(hWnd, byref(lpwndpl))
	return WindowPlacement(lpwndpl)


class __WindowEnumerator (object):
	"""
	Window enumerator class. Used internally by the window enumeration APIs.
	"""

	def __init__(self):
		self.hwnd = list()

	def __call__(self, hwnd, lParam):
		self.hwnd.append(hwnd)
		return True


class __EnumWndProc (__WindowEnumerator):
	pass


def GetLastError():
	_GetLastError = ctypes.windll.kernel32.GetLastError
	_GetLastError.argtypes = []
	_GetLastError.restype = DWORD
	return _GetLastError()


def enumWindows():
	_EnumWindows = ctypes.windll.user32.EnumWindows
	_EnumWindows.argtypes = [WNDENUMPROC, LPARAM]
	_EnumWindows.restype = bool

	EnumFunc = __EnumWndProc()
	lpEnumFunc = WNDENUMPROC(EnumFunc)
	if not _EnumWindows(lpEnumFunc, 0):
		errcode = GetLastError()
		if errcode not in (ERROR_NO_MORE_FILES, ERROR_SUCCESS):
			raise ctypes.WinError(errcode)
	return EnumFunc.hwnd


def getParent(hWnd):
	hWndParent = winUser.getAncestor(hWnd, winUser.GA_PARENT)
	# check if parent is not desktop window (desktop has no parent)
	if winUser.getAncestor(hWndParent, winUser.GA_PARENT):
		return hWndParent
	return 0


# dll handles
user32 = ctypes.windll.user32


def getExtendedWindowStyle(hwnd):
	return user32.GetWindowLongW(hwnd, winUser.GWL_EXSTYLE)
