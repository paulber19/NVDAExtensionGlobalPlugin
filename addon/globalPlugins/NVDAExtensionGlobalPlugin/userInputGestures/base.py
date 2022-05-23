# base.py
# Components required to work with input gestures collection
# A part of the NVDA Check Input Gestures add-on
# This file is covered by the GNU General Public License.
# See the file COPYING for more details.
# Copyright (C) 2021 Olexandr Gryshchenko <grisov.nvaccess@mailnull.com>

from typing import Optional, List, Iterator


class Gesture(object):
	"""Representation of one input gesture."""

	def __init__(
			self,
			gesture: str,
			category: Optional[str] = None,
			displayName: Optional[str] = None,
			className: Optional[str] = None,
			moduleName: Optional[str] = None,
			scriptName: Optional[str] = None) -> None:
		"""Initialization of the main fields of the gesture description.
		@param gesture: text representation of the input gesture
		@type gesture: str
		@param category: the category to which the gesture-related function belongs
		@type category: Optional[str]
		@param displayName: description of the gesture-related function
		@type displayName: Optional[str]
		@param className: the name of the class to which the gesture-related function belongs
		@type className: Optional[str]
		@param moduleName: the name of the module to which the associated class belongs
		@type moduleName: Optional[str]
		@param scriptName: the script name of the gesture-bound function
		@type scriptName: Optional[str]
		"""
		self._gesture = gesture or ''
		self._category = category or ''
		self._displayName = displayName or ''
		self._className = className or ''
		self._moduleName = moduleName or ''
		self._scriptName = scriptName or ''

	@property
	def gesture(self) -> str:
		"""String presentation of the input gesture.
		@return: input gesture or empty string
		@rtype: str
		"""
		return self._gesture

	@property
	def category(self) -> str:
		"""The category to which the gesture-bound function belongs.
		@return: the name of the category of the bound function or empty string
		@rtype: str
		"""
		return self._category

	@property
	def displayName(self) -> str:
		"""Text description of the gesture-bound feature.
		@return: text description of the function or empty stringn
		@rtype: str
		"""
		return self._displayName

	@property
	def className(self) -> str:
		"""Name of the class object.
		@return: class name or empty string
		@rtype: str
		"""
		return self._className

	@property
	def moduleName(self) -> str:
		"""The name of the module to which the class object belongs.
		@return: module name
		@rtype: str
		"""
		return self._moduleName

	@property
	def scriptName(self) -> str:
		"""The name of the function associated with the input gesture.
		@return: script name
		@rtype: str
		"""
		return self._scriptName

	def __eq__(self, other: object) -> bool:
		"""Comparison of objects for equality.
		@param other: an object that represents another input gesture
		@type other: object
		@return: the result of comparing the expression [self==other]
		@rtype: bool
		"""
		if not isinstance(other, Gesture):
			return False
		return self.gesture == other.gesture and self.displayName == other.displayName and \
		       self.moduleName == other.moduleName and self.scriptName == other.scriptName

	def __repr__(self) -> str:
		"""Text presentation of input gesture object.
		@return: text presentation
		@rtype: str
		"""
		return "%s - %s/%s" % (self.gesture, self.category or self.moduleName, self.displayName or self.scriptName)


class Gestures(object):
	"""Presentation of the input gestures collection."""

	def __init__(self) -> None:
		"""Initialization of internal fields."""
		self._all: List[Gesture] = []

	def __len__(self) -> int:
		"""The number of gestures in collection.
		@return: length of the collection
		@rtype: int
		"""
		return self._all.__len__()

	def __getitem__(self, index: int) -> Gesture:
		"""Gesture from the collection under a given index.
		@param index: index of the input gesture in the collection
		@type index: int
		@return: input gesture from collection under a given index
		@rtype: Gesture
		"""
		return self._all[index]

	def __iter__(self) -> Iterator[Gesture]:
		"""Iterator of Gesture objects from collection.
		@return: all Gesture objects from collection
		@rtype: Iterator[Gesture]
		"""
		for gesture in self._all:
			yield gesture

	def __contains__(self, obj: Optional[Gesture]) -> bool:
		"""Indication of whether an Gesture object is present in the collection.
		@param obj: gesture object to search in the collection
		@type obj: Optional[Gesture]
		@return: whether there is an object in the collection
		@rtype: bool
		"""
		for gesture in self._all:
			if obj == gesture:
				return True
		return False

	def append(self, obj: Gesture) -> None:
		"""Add Gesture object to the collection.
		@param obj: an input gesture that will be added to the collection
		@type obj: Gesture
		"""
		if not obj or obj in self:
			return
		self._all.append(obj)

	def initialize(self) -> None:
		"""Scan all input gestures used in NVDA.
		Procedure for scanning input gestures:
		1. Gestures binded to functions with text description (displayed in the "Input Gestures" dialog).
		2. Gestures related to functions without a text description.
		"""
		self.signed()
		self.unsigned()

	def signed(self) -> None:
		"""Scan gestures binded to functions with text description
		wich displayed in the "Input Gestures" dialog.
		"""
		import inputCore
		mapping = inputCore.manager.getAllGestureMappings()
		for category in list(mapping):
			for script in mapping[category]:
				obj = mapping[category][script]
				for gest in obj.gestures:
					gesture = Gesture(
						gesture=gest,
						category=obj.category,
						displayName=obj.displayName,
						className=obj.className,
						moduleName=obj.moduleName,
						scriptName=obj.scriptName
					)
					self.append(gesture)

	def unsigned(self) -> None:
		"""Scan gestures binded to functions without text description
		wich not displayed in the "Input Gestures" dialog.
		"""
		import globalPluginHandler
		for plugin in globalPluginHandler.runningPlugins:
			for gest, obj in plugin._gestureMap.items():
				if obj and not obj.__doc__:
					gesture = Gesture(
						gesture=gest,
						displayName=obj.__doc__,
						moduleName=obj.__module__,
						scriptName=obj.__name__.replace("script_", '')
					)
					self.append(gesture)


class FilteredGestures(object):
	"""Basic class for filtered collections of input gestures."""
	name: str = ""

	@property
	def title(self) -> str:
		"""The title of the window that displays a list of input gestures from the collection.
		@return: a text string representing the title of the window
		@rtype: str
		"""
		return self.name.replace('&', '')

	@property
	def menuItem(self) -> str:
		"""The name of the menu item that call the window to display the gesture collection.
		@return: a text string representing the name of the menu item
		@rtype: str
		"""
		return self.name + "..."

	def __len__(self) -> int:
		"""The number of input gestures in the collection.
		@return: length of the collection
		@rtype: int
		"""
		return len([item for item in self])

	def __iter__(self) -> Iterator[Gesture]:
		"""Consistently returns input gestures from the collection filtered by a certain property.
		The method must be overridden in the child class.
		@return: iterator of the filtered input gestures
		@rtype: Iterator[Gesture]
		"""
		raise NotImplementedError


class Duplicates(FilteredGestures):
	"""Collection of duplicate input gestures."""

	def __iter__(self) -> Iterator[Gesture]:
		"""Collection of the duplicated input gestures.
		@return: iterator of the duplicated input gestures
		@rtype: Iterator[Gesture]
		"""
		import config
		gestures = Gestures()
		gestures.initialize()
		collection = [gt.gesture.replace("(%s)" % config.conf['keyboard']['keyboardLayout'], '') for gt in gestures]
		for gest in gestures:
			if collection.count(gest.gesture.replace("(%s)" % config.conf['keyboard']['keyboardLayout'], '')) > 1:
				yield gest


class Unsigned(FilteredGestures):
	"""Collection of input gestures binded to functions without a text description."""

	def __iter__(self) -> Iterator[Gesture]:
		"""Collection of the unsigned input gestures.
		@return: iterator of the unsigned input gestures
		@rtype: Iterator[Gesture]
		"""
		gestures = Gestures()
		gestures.unsigned()
		for gest in gestures:
			yield gest
