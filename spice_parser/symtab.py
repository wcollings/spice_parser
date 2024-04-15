from typing import Sequence
from .linenumlist import LineNumList, LineNumNode
from fp.monad import Maybe, Empty
from fp.lists import head,tail
from .stoken import SToken, EOFToken, EOLToken

class SymTabNode:
	"""
	A node in the symbol table, which is defined as a binary tree
	"""
	left:'SymTabNode|None'
	right:'SymTabNode|None'
	contents:SToken
	""" The SToken that this symbol stores."""
	# xSymTab:int
	# """ An ID that represents the file that this symbol came from"""
	# xNode:int
	# """ An ID number for this node """
	def __init__(self, cnt:SToken) -> None:
		"""
		Parameters
		----------
		cnt:SToken
			The 'contents' of this node - the token that this symbol uniquely stores.
		xn:int
			The symbol ID number for this node
		"""
		self.contents=cnt
		self.left= None
		self.right=None
		# self.xSymTab=xst
		# self.xNode=xn

	def __del__(self):
		del self.left
		del self.right
		del self

	def __repr__(self) -> str:
		strs=[]
		if self.left:
			strs.append(str(self.left))
		strs.append(f"{self.contents}")
		if self.right:
			strs.append(str(self.right))
		return "\n".join(strs)

	def get_parent(self,tk:SToken) -> 'SymTabNode|None':
		"""
		Given some token, search all nodes below this one and find if there exists a node which is the parent of this token.

		Parameters
		----------
		tk:SToken
			The token to try to identify in the symbol table

		Returns
		-------
		Maybe[SymTabNode]
			the parent, if found, otherwise an empty monad
		"""
		node=(self.left if tk.name < self.contents.name else self.right)
		if node is not None:
			return node.get_parent(tk)
		return node

	def add(self,new_tk:SToken):
		"""
		Recursively search the Symbol Table to identify where this new token should be placed, and place it
		"""
		if self.contents==new_tk:
			self.contents=new_tk
		node=(self.left if new_tk.name < self.contents.name else self.right)
		if node is not None:
			node.add(new_tk)
		else:
			to_place = SymTabNode(new_tk)
			if node==self.left:
				self.left=to_place
			else:
				self.right=to_place
	
	def edit_value(self,name:str,val:str):
		"""
		Search the symbol table for a given symbol's name, then if found update the value in that token.

		Parameters
		----------
		name:str
			The name of the symbol to find
		val:str
			The value to store in place of the found symbol's current value

		Returns:
		bool
			Whether or not the symbol was found
		"""
		if self.contents.name==name:
			self.contents.val=val
			return True
		if self.contents.name > name and self.left:
			return self.left.edit_value(name,val)
		elif self.contents.name < name and self.right:
			return self.right.edit_value(name,val)
		return False

	def get_tok(self,name:str) -> Maybe[SToken]:
		"""
		Search the symbol table for a given symbol name

		Parameters
		----------
		name:str
			The name of the symbol to find
		
		Returns
		-------
		Maybe[SToken]
			If the symbol is found, this contains the underlying token. Otherwise this returns Empty
		"""
		if self.contents.name==name:
			return Maybe(self.contents)
		if name < self.contents.name and self.left:
			return self.left.get_tok(name)
		if name > self.contents.name and self.right:
			return self.right.get_tok(name)
		return Empty()

	def __contains__(self,tk:SToken):
		if self.contents==tk:
			return True
		if tk.name < self.contents.name and self.left:
			return self.left.__contains__(tk)
		elif tk.name > self.contents.name and self.right:
			return self.right.__contains__(tk)
		return False

class SymTab:
	"""
	A wrapper class for the Symbol Table. Provides the true interface between the binary tree and the outside.
	"""
	roots_map:dict
	roots:list
	lnl:LineNumList
	num_nodes:int
	def __init__(self) -> None:
		self.roots_map=dict()
		self.roots=[]
		self.num_nodes=0
		self.lnl=LineNumList()
	def __del__(self):
		del self.roots
	def search(self,name:str) -> SToken:
		"""
		Search for and return a token stored in the symbol table, if it exists.
		"""
		for root in self.roots:
			val=root.get_tok(name)
			if val:
				return val.val
		raise KeyError(f"{name} is not found in any symbol table!")
	def create_new_st(self,ns:str) -> int:
		next_val=len(self.roots_map)
		self.roots_map[ns]=next_val
		return next_val

	def enter(self,tk:SToken,xst:int)-> None:
		"""
		Create a symbol to store a given token, and add to the symbol table

		Parameters
		----------
		tk:SToken
			The token to store
		xst:int
			The ID of the symbol table to enter into
		"""
		if xst >len(self.roots):
			raise KeyError(f"The provided symbol table ID is invalid! {xst=}")
		if xst==len(self.roots):
			self.roots.append(tk)
		else:
			self.roots[xst].add(tk)
		self.roots[xst].add(tk)
	def edit(self,name:str,val:str,xst:int=-1):
		"""
		Find a given symbol in the symbol table and update it. If you know the symbol table ID to search, that goes in xst, otherwise you can prefix val with the namespace it belongs to, and a '.' separator, and we'll find it ourselves

		Parameters
		----------
		name:str
			The name associated with the symbol you wish to update
		val:str
			The value you wish to store intead of the current value
		"""
		if xst==-1:
			xst=self.roots_map[val.split('.')[0]]
		self.roots[xst].edit_value(name,val)
	# def __repr__(self):
		# return str(self.root)

class SymTabNS:
	parent:'SymTabNS'
	children:list['SymTabNS']
	root:SymTabNode
	name:str
	def __init__(self,name:str,root:SToken|None):
		self.children=[]
		self.name=name
		self.parent=None
		if root is not None:
			self.root=SymTabNode(root)
	def assign_root(self,root:SToken):
		self.root=SymTabNode(root)
	def add_child(self,name,root:SToken|None):
		child=SymTabNS(name,root)
		child.parent=self
		self.children.append(child)
		return child
	def add(self,tk:SToken):
		if not hasattr(self,'root'):
			self.root=SymTabNode(tk)
		else:
			self.root.add(tk)
	def __eq__(self,rhs):
		if isinstance(rhs,str):
			return self.name==rhs
		if isinstance(rhs,SymTabNS):
			return (self.name==rhs.name) or (self.root==rhs.root)
	def __getitem__(self,arg):
		if arg in self.children:
			idx=self.children.index(arg)
			return self.children[idx]
		raise LookupError(f"Namespace {arg} does not exist as a child of {self.name}!")
	def print(self):
		print(f"Namespace {self.name}")
		print(f"Children: {str(self.children)}")
		print(f"Elements:")
		print(self.root)
		print("===============")
		for child in self.children:
			child.print()
	def __repr__(self):
		return f"{self.name} (Namespace)"

def trav_ns(ns_root:SymTabNS,pth:Sequence[str]):
	if len(pth)==0:
		return ns_root
	return trav_ns(ns_root[head(pth)],tail(pth))

class SymTab2:
	roots:SymTabNS|None
	curr_ns:SymTabNS
	def __init__(self) -> None:
		self.roots=None
		self.curr_ns=self.roots
	def __del__(self):
		del self.roots
	def create_namespace(self,name:str,path=None,root_node:SToken|None=None):
		if self.roots is None:
			self.roots=SymTabNS(name,root_node)
			self.roots.parent=self.roots
			self.curr_ns=self.roots
			return self.curr_ns
		ns_parent=self.curr_ns
		if path is not None:
			ns_parent=self.roots
			for elem in path:
				ns_parent=ns_parent[elem]
		self.curr_ns=ns_parent.add_child(name,root_node)
		return self.curr_ns

	def exit_namespace(self):
		self.curr_ns=self.curr_ns.parent
	
	def enter(self,tk:SToken) -> None:
		self.curr_ns.add(tk)

	def edit(self,name:str,val:str,ns:list|None):
		if ns is None:
			ns=name.split('.')[:-1]
			name=name.split('.')[-1]
		if self.roots is None:
			return
		ns_parent=trav_ns(self.roots,ns)
		ns_parent.root.edit_value(name,val)
	def search(self,name:str,ns:list|None=None):
		if ns is None:
			ns=name.split('.')[:-1]
			name=name.split('.')[-1]
		if self.roots is None:
			return
		ns_parent=trav_ns(self.roots,ns)
		val=ns_parent.root.get_tok(name)
		if val:
			return val.val
	def print(self):
		if self.roots is not None:
			self.roots.print()

