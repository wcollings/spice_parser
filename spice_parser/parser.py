from .stoken import EOLToken, EOFToken,CommentToken, SToken
from .scanner import Scanner
from .symtab import SymTab
from .fstruct import fstruct
from .ftools import *
from os import path


class Parser:
	def __init__(self,f:str):
		start=fstruct(f)
		known_files=list_lens(fstruct.get_files(),'fname')
		if start.fname not in known_files:
			fstruct.get_files().append(start)
			start.find_dependencies()
			print(list_lens(fstruct.get_files(),'fname'))

	def get_all_files(self) -> 'list[str]':
		return fstruct.get_files()
		# return list_lens(fstruct.get_files(),'fullpath')
	def parse(self):
		# map(fstruct.parse,fstruct.get_files())
		for file in fstruct.get_files():
			file.parse()
	def write_all(self):
		for file in fstruct.get_files():
			file.write()
	def replace_val(self,name:str,val:str):
		fstruct.get_st().edit(name,val)
	def print(self):
		for file in fstruct.get_files():
			file.print()
	def get_symtab(self):
		return fstruct.get_st()
	def get_symbol(self,name:str):
		sym=fstruct.get_st().search(name)
		if sym:
			return {"name":sym.name,"val":sym.val}
		raise KeyError(f"{name} not found in symbol table!")
	def clear_files(self):
		fstruct.clear_files()

