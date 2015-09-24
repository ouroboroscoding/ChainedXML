# coding=utf8
##@package dvtl2-lib
#
# XML module
#
# Wraps cELementTree classes into a more easily usable interface
#
# @author Chris Nasr
# @copyright Gaargle Solutions
# @created 2015-09-10

# Import python core modules
import xml.etree.ElementTree as ET
from StringIO import StringIO

## New
#
# Starts a new XML document and returns a pointer to use for adding additional
# elements
#
# @name new
# @param string declaration				If set must be a valid charset
# @param string root					If set must be the name of the root element
# @return _CWrapper
def new(declaration=False, root=None):

	# Create a new instance
	oRet	= _CWrapper()

	# If the root is set, create it
	if root:

		# Create a new root element
		oRet.add(root)

	# If we have a declaration
	if declaration:

		# Set the declaration
		oRet.declaration	= declaration

	# Return the new _CWrapper
	return oRet

## Linked Element
#
# Extends the functionality of Element to add the ability to go up the tree
# as well as down
#
# @name _LinkedElement
# @extends ET.Element
class _CLinkedElement(ET.Element):

	## Appened
	#
	# Overrides Element.append to add the parent so we can traverse up and down
	# the element tree
	#
	# @name append
	# @param _CLinkedElement self		A pointer to the current instance
	# @param _CLinkedElement element	The element to append to this instance
	# @return
	def append(self, element):

		# Set the element's parent to the current instance
		element.parent(self)

		# Call the base classes append method
		return super(_CLinkedElement,self).append(element)

	## Parent
	#
	# Get or set the parent element
	#
	# @name parent
	# @param _LinkedElement self		A pointer to the current instance
	# @param Element setter				If set, method is a setter not a getter
	# @return Element|None
	def parent(self, setter=None):

		# If we are setting the parent
		if setter is not None:
			self._parent	= setter

		# Else if we are getting the parent
		else:
			try:
				return self._parent
			except AttributeError:
				return None

## CDATA
#
# Special type for <![CDATA[]]> Elements
#
# @name CDATA
# @param str text					The text to encapsulate
# @return ET.Element
def _CDATA(text=None):

	# Create the new Element
	oElem		= _CLinkedElement('![CDATA[')

	# Set the text
	oElem.text	= text

	# Return it
	return oElem

# Save the original serialize XML so we can use it within our custom one
_serialize_xml_default	= ET._serialize_xml

## CDATA Serialize XML
#
# Handles CDATA elements properly and hands everything else off to the default
# serialized
#
# @name _cdata_serialize_xml
# @param function method				The method to use to write the serialized text
# @param _CLinkedElement elem			The element to serialize
# @param str encoding					The encoding to use
def _cdata_serialize_xml(method, elem, encoding,  qnames, namespaces):

	global _serialize_xml_default

	# If we have the special CDATA Element
	if elem.tag == '![CDATA[':
		method("<%s%s]]>" % (elem.tag, elem.text))

	# Else it's a regular Element
	else:
		return _serialize_xml_default(method, elem, encoding, qnames, namespaces)

# Change the internal _serialize_xml function to our custom one
ET._serialize_xml = ET._serialize['xml'] = _cdata_serialize_xml

## Wrapper
#
# XML Wrapper class to simplify the generation and saving of XML files
#
# @name _CWrapper
# @extends object
class _CWrapper(object):

	## Constructor
	#
	# Initialises the instance
	#
	# @name _CWrapper
	# @param _CWrapper self				A pointer to the current instance
	# @return _CWrapper
	def __init__(self, declaration=False):
		self._current		= None
		self._root			= None
		self.declaration	= ''

	## Add
	#
	# Add an element to the currently selected element
	#
	# @name add
	# @param _CWrapper self				A pointer to the current instance
	# @param string name				The name of the element to create
	# @param dict attr					A dictionary of attributes to add
	# @param str text					The text within the element
	# @param bool set_as_last			If true, the new element will become the currently select
	# @return _CWrapper
	def add(self, name, attr=None, text=None, cdata=None, current=True):

		# Set current
		bCurr	= current

		# Create the element
		oElem	= _CLinkedElement(name)

		# If there's any attributes
		if isinstance(attr, dict):

			# Go through each attribute
			for k,v in attr.iteritems():

				# And add it to the element
				oElem.set(k, v)

		# If there's any text
		if text:

			# Set it
			oElem.text	= text

			# Don't set as current
			bCurr	= False

		# Else If there's CDATA
		elif cdata:

			# Create a CDATA Element
			oCData	= _CDATA(cdata)

			# Add it to the element
			oElem.append(oCData)

			# Don't set as current
			bCurr	= False

		# If there's no current element
		if self._current is None:

			# Store it as the root and current
			self._root		= oElem
			self._current	= oElem

		# Else if we have a current element
		else:

			# Add it to the current
			self._current.append(oElem)

		# If this needs to be the new current
		if bCurr:

			# Store it
			self._current	= oElem

		# Return itself for chaining
		return self

	## Generate
	#
	# Returns the XML as a string
	#
	# @name generate
	# @param _CWrapper self				A pointer to the current instance
	# @return str
	def generate(self):

		# If we have no root
		if self._root is None:
			raise Exception('No root element')

		# Create a new tree
		xmlRoot	= ET.ElementTree(self._root)

		# Create a string that works like a file
		ioXML	= StringIO()

		# If we have declaration
		if self.declaration:

			# Write the XML with the declaration
			xmlRoot.write(ioXML, self.declaration, True)

		# Else
		else:

			# Write the XML without the declaration
			xmlRoot.write(ioXML)

		# Return the string
		return ioXML.getvalue()

	## Root
	#
	# Sets the root to the currently selected Element
	#
	# @name root
	# @param _CWrapper self				A pointer to the current instance
	# @return _CWrapper
	def root(self):

		# If we don't have a root Element
		if self._root is None:
			raise Exception('No root element')

		# Set the root Element as the current Element
		self._current	= self._root

		# Return itself for chaining
		return self

	## Up
	#
	# Sets the current Element as the parent of the current Element
	#
	# @name up
	# @param _CWrapper self				A pointer to the current instance
	# @return _CWrapper
	def up(self):

		# Find out the parent of the current element
		oParent	= self._current.parent()

		# If we have no current element, raise an exception
		if oParent is None:
			raise Exception('Nothing above current element')

		# Set the current to the parent
		self._current	= oParent

		# Return itself for chaining
		return self