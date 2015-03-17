import re
import unittest

class ParseError(Exception):
	def __init__(self, frmt, failStr, *msg):
		message = "Failed to format input '" + str(failStr) + "' with " +\
			" format '" + str(frmt) + "'."

		# Add any extra messages
		for extraMsg in msg:
			message += "\n" + extraMsg

		super(ParseError, self).__init__(message)

class FormatError(Exception):
	def __init__(self,  frmt, *msg):
		message = "Format Error."

		# Add any extra messages
		for extraMsg in msg:
			message += " " + extraMsg

		super(FormatError, self).__init__(message)

""" Helper for splitting field specifier into width and type """
fieldRe = re.compile(r"%([0-9]*)([a-z]+)") # Match format specifiers

def tryFunc(s, func):
	try:
		return func(s)
	except ValueError:
		return s

FORMATS = {
# Specifier : Function(str) = value
	"d"		: int,
	"s"		: str,
	"x"		: lambda s: int(s, 16),
	"f"		: float
}

def formatValue(value, ftype):
	try:
		func = FORMATS[ftype]
	except KeyError, e:
		raise FormatError("%"+ftype, str(e))

	try:
		fval = func(value)
		return fval
	except ValueError,e:
		raise ParseError("%"+ftype, value, str(e))

class RecordDescriptor(object):
	""" Defines how a record's contents should be unpacked into key/value 
	pairs. """
	INFO_RECORD = "INFO_RECORD"
	EVENT_RECORD = "EVENT_RECORD"
	RECORD_TYPES = [INFO_RECORD, EVENT_RECORD]

	def __init__(self, recordType, *args):
		""" At the minimum, a descriptor needs a key and a recordType. This
		indicates which record it describes. The recordType should be one of
		[%s]. This indicates how and when the record should be handled. An arg 
		should be provided for each field in the record following the key. 
		These fields are comma-delimited, i.e:
		"key,arg1,arg2,..."
		""" % ",".join(self.RECORD_TYPES)

		assert recordType.upper() in self.RECORD_TYPES, \
			"recordType must be one of [%s]" % ",".join(self.RECORD_TYPES)
		self.recordType = recordType
		self.names  = []
		self.fields = []
		for arg in args:
			self.add_arg(arg)

	def add_arg(self, frmt, *names):
		""" names are the the key that are used in the result dictionary of
		unpack. It also makes names required keyword arguments for pack. 
		Format is essentially a printf style format, but with a caveat - 
		Fixed-width fields are prioritized over greedy fields. Examples:
		%3d is an integer field with character width 3
		%3d%d%3d unpacks a variable amount of characters, but allows matches
		with the fixed width parameters if possible.
		123456789 --> %3d%d%3d --> [123, 456, 789]
		1234567   --> %3d%d%3d --> [123,   4, 567]
		123456    --> %3d%d%3d --> ParseError, %d must match something!
		123abc456 --> %3d%s%3d --> [123, "abc", 456]
		Multiple variable length fields are forbidden.
		i.e. all these are ParseError: %d%d , %d%s , %s%3d%s
		"""

		frmts = fieldRe.findall(frmt)
		if len(frmts) != len(names):
			raise FormatError(frmt, "Need as many arguments as format specs.")

		self.names  += [ tuple(names) ]
		self.fields += [ frmt ]
		
	def add_descriptor(self, desc, name):
		self.names += [ name ]
		self.fields += [ desc ]

	def unpack(self, recordLine):
		""" Unpacks a record based on the descriptor. recordLine should contain
		a line from an event file containing a record. Returns a dictionary
		describing the contents of the record. """

		elements = [elem.strip() for elem in recordLine.split(",")]
		result = {}
		# if len(elements) != len(self.fields):
		# 	raise ParseError(str(self.fields), str(elements),
		# 		("# of fields in record (%d) " % len(elements)) + \
		# 		"does not match # of fields in " + \
		# 		"descriptor (%d)." % len(self.fields))
		
		for (field, elem, name) in zip(self.fields, elements, self.names):

			# Find all the format specifiers
			frmts = fieldRe.findall(field)

			def processChunk(reverse=False):
				values = []
				text_index = 0
				# Reverse the text to make it easier to parse the right-align
				text = elem[::-1] if reverse else elem
				for frmtIndex in sorted(range(len(frmts)), reverse=reverse):
					(width, ftype) = frmts[frmtIndex]

					if width != "":
						width = int(width) # Ensure width is a number
						# Get a text piece with size "width"
						valuetext = text[text_index:text_index + width]
						# Unreverse the text if necessary
						value = valuetext[::-1] if reverse else valuetext
						# Move the text cursor
						text_index += width
						# Format the value based on the specifier in frmt
						value = formatValue(value, ftype)
						# Add it to the list of extracted values
						values += [value]
					else:
						break

				# Unreverse everything if necessary
				text_index = len(elem)-text_index if reverse else text_index
				values = values[::-1] if reverse else values
				return (values, text_index)


			# Read in the left-aligned fields
			(lalign_values, lalign_end) = processChunk()

			if lalign_end < len(elem):
				# Read in the right-aligned fields:
				(ralign_values, ralign_end) = processChunk(reverse=True)
				# Check to see that they ended at the same place
				if len(ralign_values) + len(lalign_values) + 1 < len(frmts):
					raise FormatError(field)
				# now we have the variable length text
				(dummy, ftype) = frmts[len(lalign_values)]
				var_text = elem[lalign_end:ralign_end]
				values = lalign_values + \
					[ formatValue(var_text, ftype) ] + ralign_values
			elif len(elem) == 0:
				if len(frmts) > 1:
					raise ParseError(field, elem)
				else:
					(dummy, ftype) = frmts[0]
					values = [ formatValue(elem, ftype) ]
			else:
				values = lalign_values

			# We finally have our list of values, map them to names and add it
			# to the result dictionary
			result.update({ key : value for (key, value) in zip(name, values)})

		return result


	def pack(self, **kargs):
		""" Packs a record based on the descriptor. All necessary arguments
		need recordLine should contain
		a line from an event file containing a record. Returns a dictionary
		describing the contents of the record. """
		result = []
		for (field, name) in zip(self.fields, self.names):

			# Find all the format specifiers
			frmts = fieldRe.findall(field)
			frmts = ["%" + "".join(frmt) for frmt in frmts]

			# Write each format in order
			packedResult = ""
			for (frmt, key) in zip(frmts, name):
				frmt = frmt.replace("td", "d")
				packedResult += frmt % kargs[key]

			result += [packedResult]

		return ",".join(result)



