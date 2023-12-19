from .linenumlist import LineNumList, LineNumNode
from .monad import Maybe, Empty
from .stoken import SToken, EOFToken, EOLToken

class SymTabNode:
	"""
	A node in the symbol table, which is defined as a binary tree
	"""
	left:'Maybe[SymTabNode]'
	right:'Maybe[SymTabNode]'
	contents:SToken
	""" The SToken that this symbol stores."""
	xSymTab:int
	""" An ID that represents the file that this symbol came from"""
	xNode:int
	""" An ID number for this node """
	def __init__(self, cnt:SToken,xst:int,xn:int) -> None:
		"""
		Parameters
		----------
		cnt:SToken
			The 'contents' of this node - the token that this symbol uniquely stores.
		xst:int
			The ID of the file this symbol comes from
		xn:int
			The symbol ID number for this node
		"""
		self.contents=cnt
		self.left= Empty()
		self.right=Empty()
		self.xSymTab=xst
		self.xNode=xn

	def __del__(self):
		del self.left
		del self.right
		del self

	def __repr__(self) -> str:
		strs=[]
		if self.left:
			strs.append(str(self.left))
		strs.append(f"{self.contents}:{self.xSymTab}.{self.xNode}")
		if self.right:
			strs.append(str(self.right))
		return "\n".join(strs)

	def get_parent(self,tk:SToken) -> 'Maybe[SymTabNode]':
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
		if node:
			return Maybe(node.val.get_parent(tk))
		return node

	def add(self,new_tk:SToken,xst:int,xnn:int):
		"""
		Recursively search the Symbol Table to identify where this new token should be placed, and place it
		"""
		if self.contents==new_tk:
			self.contents=new_tk
		node=(self.left if new_tk.name < self.contents.name else self.right)
		if node:
			node.val.add(new_tk,xst,xnn)
		else:
			if node==self.left:
				self.left=Maybe(SymTabNode(new_tk,xst,xnn)) #0s for now
			else:
				self.right=Maybe(SymTabNode(new_tk,xst,xnn)) #0s for now
	
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
			return self.left.val.edit_value(name,val)
		elif self.contents.name < name and self.right:
			return self.right.val.edit_value(name,val)
		return False

	def get_tok(self,name:str):
		"""
		Search the symbol table for a given symbol name

		Parameters
		----------
		name:str
			The name of the symbol to find
		
		Returns
		-------
		Maybe[SymTabNode]
			If the symbol is found, this contains the underlying token. Otherwise this returns Empty
		"""
		if self.contents.name==name:
			return self.contents
		if name < self.contents.name and self.left:
			return self.left.val.get_tok(name)
		if name > self.contents.name and self.right:
			return self.right.val.get_tok(name)
		return Empty()

	def __contains__(self,tk:SToken):
		if self.contents==tk:
			return True
		if tk.name < self.contents.name and self.left:
			return self.left.val.__contains__(tk)
		elif tk.name > self.contents.name and self.right:
			return self.right.val.__contains__(tk)
		return False

class SymTab:
	"""
	A wrapper class for the Symbol Table. Provides the true interface between the binary tree and the outside.
	"""
	root:Maybe[SymTabNode]
	lnl:LineNumList
	num_nodes:int
	def __init__(self) -> None:
		self.root=Empty()
		self.num_nodes=0
		self.lnl=LineNumList()
	def __del__(self):
		del self.root
	def search(self,name:str):
		"""
		Search for and return a token stored in the symbol table, if it exists.
		"""
		return self.root.val.get_tok(name)

	def enter(self,tk:SToken)-> None:
		"""
		Create a symbol to store a given token, and add to the symbol table

		Parameters
		----------
		tk:SToken
			The token to store
		"""
		if not self.root:
			self.root=Maybe(SymTabNode(tk,0,self.num_nodes))
		elif tk not in self.root.val:
			self.num_nodes+=1
		self.root.val.add(tk,0,self.num_nodes)
	def edit(self,name:str,val:str):
		"""
		Find a given symbol in the symbol table and update it

		Parameters
		----------
		name:str
			The name associated with the symbol you wish to update
		val:str
			The value you wish to store intead of the current value
		"""
		self.root.val.edit_value(name,val)
	def __repr__(self):
		return str(self.root)
