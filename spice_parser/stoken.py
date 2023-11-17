"""
Contains token types and definitions for the SPICE Scanner
"""
from .linenumlist import LineNumNode
class SToken:
	"""
	Generic token type. If the token is a key-value pair (e.g. "R=0.2"), both fields are recorded, otherwise only the key is.
	"""
	name:str
	val:str
	lineno:LineNumNode
	def __init__(self,name:str,val:str,ln:LineNumNode=LineNumNode(-1)):
		"""
		Parameters
		----------
		name:str
			The name (key) of the token
		val:str
			If this is part of a key-value pair, the value associated with this key
		ln:LineNumNode
			The line number that this token is initially defined on
		"""
		self.name=name
		self.val=val
		self.lineno=ln
	def __repr__(self):
		if self.val != "":
			#return f"name={self.name}\tval={self.val} (Token)"
			return f"{self.name}={self.val}"
		#return f"{self.name} (Token)"
		return self.name
	def __eq__(self, __value: 'SToken|str') -> bool:
		if isinstance(__value,SToken):
			return self.name==__value.name
		return self.name==__value
	def write(self,f):
		"""
		Given an open file pointer, write this token to disk. Deprecated!
		"""
		f.write(self.name)
		if self.val:
			f.write("="+self.val)
		f.write(" ")
		raise DeprecationWarning



class EOFToken(SToken):
	"""
	A token representing the end of the current file
	"""
	def __init__(self, ln:LineNumNode):
		super().__init__("EOFToken","",ln)
	def __repr__(self):
		return ""
		#return "\n----------END OF FILE----------\n"
	def write(self,f):
		f.write("\n")


class EOLToken(SToken):
	"""
	A token representing the end of a line (or series of lines, if continued) in the current file
	"""
	def __init__(self, ln:LineNumNode):
		super().__init__("EOLToken","",ln)
	def __repr__(self):
		return '\n'
	def write(self,f):
		f.write("\n")

class CommentToken(SToken):
	"""
	A token representing a line comment
	"""
	def __init__(self,val,ln:LineNumNode):
		super().__init__("Comment",val,ln)
	def __repr__(self):
		return self.val
	def write(self,f):
		f.write(self.val)
		#f.write('\n')
