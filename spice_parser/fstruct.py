from .stoken import *
from .scanner import Scanner
from .symtab import SymTab
from .monad import Counter
from os import path, stat
from functools import reduce

def rem(s:str,old:str) -> str:
	rep=lambda s,r:str.replace(s,r,"")
	return reduce(rep,[s]+list(old))

files=[]
st=SymTab()
class fstruct:
	lines:list
	fname:str
	pth:str
	xid:int
	scn:Scanner
	ignore:bool
	parsed:bool
	dependencies:list
	""" If this is a text file, we shouldn't try to parse it or write it like a spice file"""
	def __init__(self,fname,pth="", ignore=False):
		if fname.startswith('"') and fname.endswith('"'):
			fname=fname[1:-1]
		self.pth,self.fname=path.split(fname)
		if pth != "":
			self.pth=path.join(pth,self.pth)
		if self.pth=="":
			self.pth="."
		self.fullpath=path.join(self.pth,self.fname)
		self.scn=Scanner(self.fullpath)
		if not ignore:
			ns=fname.split("/")[-1].split('.')[0]
			self.ns=st.curr_ns
			# self.ns=st.create_namespace(ns)
		self.lines=[]
		# self.fullpath=path.join(self.pth,self.fname)
		self.scn=None #pyright:ignore
		self.ignore=ignore
		self.write_end=False
		self.parsed=False
		self.dependencies=[]
	def __repr__(self):
		return f"{self.fname} (fstruct)"

	def recenter(self,pth,suffix:str=""):
		if suffix!="":
			parts=self.fname.split('.')
			self.fname=parts[0]+suffix+'.'+parts[1]
		self.pth=pth
		self.fullpath=path.join(self.pth,self.fname)
		for file in self.dependencies:
			fname=rem(file.val,"'\"").split('/')[-1]
			if suffix!="":
				parts=fname.split('.')
				fname=parts[0]+suffix+'.'+parts[1]
			file.val='"'+fname+'"'

	def write(self):
		if self.ignore:
			return
		lines_to_write = []
		with open(self.fullpath, 'w') as f:
			for line in self.lines:
				line.write(f)
			if self.write_end:
				f.write(".end")
	def find_dependencies(self):
		fnames=list_lens(files,'fname')
		try:
			self.scn=Scanner(self.fullpath)
		except:
			print(f"File: {self.fullpath} does not exist!")
		for tk in self.scn:
			if tk.name.lower() in ['.inc','.lib'] and self.scn.len_of_line()==3:
				f_to_find=fstruct(self.scn.peek().name,self.pth)
				if not f_to_find.fname in fnames:
					files.append(f_to_find)
					f_to_find.find_dependencies()
			elif tk.name.lower()=="pwlfile":
				f_to_find=fstruct(tk.val,self.pth,ignore=True)
				if not f_to_find.fname in fnames:
					files.append(f_to_find)
		self.scn.reset()
	def parse(self):
		if self.parsed:
			return
		if self.ignore:
		# 	delim=" "
		# 	lines=open(self.fullpath,'r').readlines()
		# 	if "," in lines[0]:
		# 		delim=','
		# 	lines=[line.split(delim) for line in lines]
		# 	self.delim=delim
			return
		st.curr_ns=self.ns
		# self.scn=Scanner(self.fullpath)
		while not (isinstance(elem:=next(self.scn),EOFToken)):
			opts=[]
			if isinstance(elem, CommentToken):
				self.lines.append(elem)
				continue
			elif isinstance(elem, EOLToken):
				continue
			# elif elem.name.lower() == ".end":
				# self.write_end=True
				# st.exit_namespace()
			name=elem.name.lower()
			if name[0] in "rclgefhvidx":
				self.lines.append(ElementToken(elem,self.scn))
			elif name == ".lib" and self.scn.len_of_line()==2:
				self.lines.append(LibToken(next(self.scn),self.scn, st))
			elif name in ['.inc', '.lib'] and self.scn.len_of_line()==3:
				tk=IncludeToken(self.scn)
				self.dependencies.append(tk)
				self.lines.append(tk)
			elif name.startswith("."):
				self.lines.append(OptionToken(elem,self.scn))
		for elem in self.lines:
			if not isinstance(elem,CommentToken):
				elem.add_to_st(st)
		self.parsed=True
		st.exit_namespace()
	def print(self):
		print("-----------------------")
		print(self.fname)
		print("-----------------------")
		for line in self.lines:
			print(line)
	@staticmethod
	def get_files():
		return files
	@staticmethod
	def get_st():
		return st
	@staticmethod
	def clear_files():
		global files
		for file in files:
			del file
		files=[]
