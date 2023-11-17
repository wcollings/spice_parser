from .stoken import EOLToken, EOFToken,CommentToken, SToken
from .scanner import Scanner
from .symtab import SymTab
from os import path

st=SymTab()
files=[]
class fstruct:
	lines:list
	fname:str
	pth:str
	xid:int
	scn:Scanner
	ignore:bool
	""" If this is a text file, we shouldn't try to parse it or write it like a spice file"""
	def __init__(self,fname,pth="", ignore=False):
		if fname.startswith('"') and fname.endswith('"'):
			fname=fname[1:-1]
		self.pth,self.fname=path.split(fname)
		if pth != "":
			self.pth=path.join(pth,self.pth)
		self.xid=len(files)+1
		self.lines=[]
		self.fullpath=path.join(self.pth,self.fname)
		self.scn=None #pyright:ignore
		self.ignore=ignore
	def __del__(self):
		if self.scn:
			del self.scn
		del self.lines

	def write(self):
		if self.ignore:
			return
		lines_to_write = []
		for line in self.lines:
			elems=[str(e) for e in line[:-1]]
			full_line=" ".join(elems)
			if isinstance(line[0],CommentToken):
				lines_to_write.append(elems[0])
			elif len(full_line) > 90:
				buff=[elems[0]]
				for elem in full_line.split(' ')[1:]:
					if (len(" ".join(buff)) + len(elem) < 89):
						buff.append(elem)
					else:
						lines_to_write.append(" ".join(buff))
						buff=["+", elem]
				lines_to_write.append(" ".join(buff))
			else:
				lines_to_write.append(" ".join(elems))
		with open(self.fullpath, 'w') as f:
			for ltw in lines_to_write:
				f.write(ltw)
				f.write('\n')
	def find_dependencies(self):
		fnames=[f.fname for f in files]
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
	def parse(self):
		if self.ignore:
			delim=" "
			lines=open(self.fullpath,'r').readlines()
			if "," in lines[0]:
				delim=','
			lines=[line.split(delim) for line in lines]
			self.delim=delim
			return
		self.scn=Scanner(self.fullpath)
		elem=[]
		if len(self.lines) != 0:
			return
		for tk in self.scn:
			elem.append(tk)
			if isinstance(tk,EOLToken):
				self.lines.append(elem)
				elem=[]
			st.enter(tk)
		self.lines.append(elem)
	def print(self):
		print("-----------------------")
		print(self.fname)
		print("-----------------------")
		for line in self.lines:
			print(" ".join([str(e) for e in line]))


class Parser:
	def __init__(self,f:str):
		start=fstruct(f)
		known_files=[f.fname for f in files]
		if start.fname not in known_files:
			files.append(start)
			start.find_dependencies()
		# print("Found files:")
		# for file in files:
			# print(file.fname)

	def get_all_files(self) -> 'list[str]':
		return [f.fullpath for f in files]
	def parse(self):
		for file in files:
			file.parse()
	def write_all(self):
		for file in files:
			file.write()
	def replace_val(self,name:str,val:str):
		st.edit(name,val)
	def print(self):
		for file in files:
			file.print()
	def get_symtab(self):
		return st
	def get_symbol(self,name:str):
		sym=st.search(name)
		if sym:
			return {"name":sym.name,"val":sym.val}
		raise KeyError(f"{name} not found in symbol table!")
