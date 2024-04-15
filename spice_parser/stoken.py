"""
Contains token types and definitions for the SPICE Scanner
"""
from enum import Enum
from typing import Protocol, Any
from .linenumlist import LineNumNode
from .monad import Maybe, Empty
from .ftools import list_lens

#-----------#
# Protocols #
#-----------#
class Tok(Protocol):
	name:str
	val:Any
	def __init__(self) -> None: ...
class SymTab(Protocol):
	def enter(self, tk:Tok) -> None: ...
	def create_namespace(self,name:str,path=None,root_node:Tok|None=None): ...
	def exit_namespace(self): ...

class tokenizer(Protocol):
	curr_xst:int
	def __next__(self) -> 'SToken': ...
	def peek(self) -> 'SToken': ...
	def len_of_line(self) -> int: ...
class CmdToken(Protocol):
	def write(self,f)->None: ...
	def continue_parse(self,p:tokenizer) -> None: ...
	def add_to_st(self,st:SymTab) -> None: ...

class SToken:
	"""
	Generic token type. If the token is a key-value pair (e.g. "R=0.2"), both fields are recorded, otherwise only the key is.
	"""
	name:str
	val:str
	lineno:LineNumNode
	def __init__(self,name:str,val:str|None=None,ln:LineNumNode=LineNumNode(-1)):
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
		if val is not None:
			self.val=val
		self.lineno=ln
	def __repr__(self):
		if self.val != "":
			return f"{self.name}={self.val}"
		return self.name
	def __eq__(self, _value: 'SToken|str') -> bool:
		if isinstance(_value,SToken):
			return self.name==_value.name
		return self.name==_value
	def write(self,f):
		"""
		Given an open file pointer, write this token to disk. Deprecated!
		"""
		raise DeprecationWarning
		f.write(self.name)
		if self.val:
			f.write("="+self.val)
		f.write(" ")


#-------------------------#
# Nonprinting token types #
#-------------------------#
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

class EOFToken(EOLToken):
	"""
	A token representing the end of the current file
	"""
	def __init__(self, ln:LineNumNode=LineNumNode(-1)):
		super().__init__(ln)
	def __repr__(self):
		return ""
		#return "\n----------END OF FILE----------\n"
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
		f.write(self.val+'\n')
	def add_to_st(self,st:SymTab):
		pass


#----------------#
# Element tokens #
#----------------#

class ElementToken:
	name:str
	legs:list[SToken]
	val:SToken
	opts:list[SToken]
	def __init__(self,name:SToken,parser:tokenizer|None=None) -> None:
		self.name=name.name
		self.legs=[]
		self.opts=[]
		if parser:
			self.continue_parse(parser)
	def write(self,f):
		legs=' '.join(map(str,self.legs))
		opts=' '.join(map(str,self.opts))
		if not hasattr(self,"val"):
			print(self.name + " has no val!")
			print(self.legs)
			print(self.opts)
		f.write(f"{self.name} {legs} {self.val} {opts}\n")
	def continue_parse(self,p:tokenizer):
		while not p.peek().val and not isinstance(p.peek(),EOLToken):
			self.legs.append(next(p))
		try:
			self.val=self.legs.pop()
		except:
			print("Parsing " + self.name, end=":")
			print("No legs found, so this fails!")
		while not isinstance(p.peek(),EOLToken):
			self.opts.append(next(p))
		next(p)
	def add_to_st(self,st:SymTab):
		st.enter(self) #pyright:ignore
	def __repr__(self):
		return ' '.join([self.name] + list_lens(self.legs,'name') + [str(self.val)])

class SubcktToken:
	params:list[CmdToken]
	xst:int
	def __init__(self,parser:tokenizer):
		self.name=next(parser).name
		self.ports=[]
		while not parser.peek().val and not isinstance(parser.peek(),EOLToken):
			self.ports.append(next(parser))
		self.params=[]
		self.comps=[]
		next(parser)
		self.continue_parse(parser)
	def add_params(self,params:list[CmdToken]):
		self.params=params
	def add_comp(self,comp:ElementToken):
		self.comps.append(comp)
	def continue_parse(self,p:tokenizer) -> None:
		while p.peek().name != ".ends":
			elem=next(p)
			if isinstance(elem, EOLToken):
				continue
			if isinstance(elem,CommentToken):
				self.comps.append(elem)
			elif elem.name.lower() in [".inc",".lib"] and p.len_of_line()==3:
				self.comps.append(IncludeToken(p))
			elif elem.name.startswith("."):
				self.params.append(OptionToken(elem,p))
			elif elem.name[0].lower() in "rclgefhvidx":
				self.comps.append(ElementToken(elem,p))
		next(p)
		next(p)
	def add_to_st(self,st:SymTab):
		st.create_namespace(self.name,root_node=self) # pyright:ignore
		for comp in self.comps:
			comp.add_to_st(st)
		for param in self.params:
			param.add_to_st(st)
		# st.enter(self) # pyright:ignore
		st.exit_namespace()
	def __repr__(self) -> str:
		return ' '.join([self.name] + list_lens(self.ports,'name'))


	def write(self,f):
		ports=" ".join([str(p) for p in self.ports])
		f.write(f".subckt {self.name} {ports}\n")
		if self.params:
			for param in self.params:
				param.write(f)
		if self.comps:
			for comp in self.comps:
				comp.write(f)
				# f.write(comp + '\n')
		f.write('.ends\n')

class LibToken:
	subckts:list[SubcktToken]
	name:str
	def __init__(self,name:SToken,parser:tokenizer, st):
		self.name=name.name
		self.subckts=[]
		self.continue_parse(parser)
	def write(self,f):
		f.write(f".LIB {self.name}\n")
		for subckt in self.subckts:
			subckt.write(f)
		f.write(".endl\n")
	def continue_parse(self, p:tokenizer) -> None:
		while not p.peek().name.lower() ==".endl":
			next(p)
			next(p)
			self.subckts.append(SubcktToken(p))
		next(p)
	def add_to_st(self,st:SymTab):
		st.create_namespace(self.name,root_node=self) #pyright:ignore
		for subct in self.subckts:
			subct.add_to_st(st)
		st.exit_namespace()
	def __repr__(self):
		return f"{self.name} (LIB entry)"

class IncludeToken:
	xst:int
	def __init__(self,parser:tokenizer):
		self.val=next(parser).name
		self.name=next(parser).name
	def write(self,f):
		f.write(f'.lib {self.val} {self.name}\n')
	def add_to_st(self,st:SymTab):
		st.enter(self)
	def __repr__(self) -> str:
		return f".lib {self.val} {self.name}"

class OptionToken:
	opts:list[SToken]
	name:str
	def __init__(self,name:SToken,parser:tokenizer):
		self.opts=[]
		self.name=name.name
		self.continue_parse(parser)
	def write(self,f):
		f.write(self.name + " ")
		if self.opts:
			for line in generate_line_splits(self.opts):
				f.write(line+'\n')
	
	def continue_parse(self,p:tokenizer) -> None:
		while not isinstance(p.peek(),EOLToken):
			self.opts.append(next(p))
		next(p)
	def add_to_st(self, st:SymTab):
		for opt in self.opts:
			st.enter(opt)
	def __repr__(self) -> str:
		return self.name + f"... ({len(self.opts)} values)"
def generate_line_splits(inp:list[SToken]):
	elems=[str(e) for e in inp]
	output=[]
	full_line=" ".join(elems)
	if isinstance(inp[0],CommentToken):
		output.append(elems[0])
	elif len(full_line) > 90:
		buff=[elems[0]]
		for elem in full_line.split(' ')[1:]:
			if (len(" ".join(buff)) + len(elem) < 89):
				buff.append(elem)
			else:
				output.append(" ".join(buff))
				buff=["+", elem]
		output.append(" ".join(buff))
	else:
		output.append(" ".join(elems))
	return output
