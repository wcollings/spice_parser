from .stoken import EOLToken, EOFToken,CommentToken, SToken
from .scanner import Scanner
from .symtab import SymTab
from .fstruct import fstruct
from .ftools import *
from os import path


class Parser:
	"""
	The parser module, which is public-facing.
	"""
	def __init__(self,f:str):
		"""
		Parameters
		----------
		f:str
			The file name of the main SPICE file
		"""
		start=fstruct(f)
		st=start.get_st()
		name=start.fname.split("/")[-1].split('.')[0]
		start.ns=st.create_namespace(name)
		known_files=list_lens(fstruct.get_files(),'fname')
		if start.fname not in known_files:
			fstruct.get_files().append(start)
			start.find_dependencies()
			# print(list_lens(fstruct.get_files(),'fname'))

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
		return fstruct.get_st().search(name)
	def clear_files(self):
		fstruct.clear_files()
	def set_root(self,pth:str, suffix:str=""):
		for file in fstruct.get_files():
			file.recenter(pth,suffix)
