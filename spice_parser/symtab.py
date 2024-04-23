from typing import Sequence
from .linenumlist import LineNumList, LineNumNode
from fp.monad import Default, Maybe, Empty
from fp.lists import head,tail
from .stoken import SToken, EOFToken, EOLToken
class Counter:
	curr=0
	def __init__(self):
		self.curr=-1
	def __call__(self) -> int:
		self.curr+=1
		return self.curr
counter=Counter()

class SymTabNode:
	"""
	A node in the symbol table, which is defined as a binary tree
	"""
	left:'SymTabNode|None'
	right:'SymTabNode|None'
	parent:'SymTabNode|None'
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
		"""
		self.contents=cnt
		self.left= None
		self.right=None
		self.parent=None

	def __del__(self):
		del self.left
		del self.right
		del self

	def __repr__(self) -> str:
		strs=[]
		bf=self.bf()
		# bf=0
		return f"{self.contents} ({bf=})"
		if self.left:
			strs.append(str(self.left))
		strs.append(f"{self.contents}")
		if self.right:
			strs.append(str(self.right))
		return "\n".join(strs)

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
			node=("left" if new_tk.name < self.contents.name else "right")
			to_place = SymTabNode(new_tk)
			to_place.parent=self
			if node=="left":
				self.left=to_place
			else:
				self.right=to_place
		bf=self.bf()
		if bf<-1:
			if self.left.bf() > 0: #pyright:ignore
				self.left.lrot() #pyright:ignore
			self.rrot()
				
		elif bf>1:
			if self.right.bf()<0: #pyright:ignore
				self.right.rrot() #pyright:ignore
			self.lrot()
		pass

	def lrot(self):
		sr=self.right
		if sr is None:
			return
		self.right=sr.left
		if sr.left is not None:
			sr.left.parent=self
		if self.parent is not None:
			if self.parent.right==self:
				self.parent.right=sr
			else:
				self.parent.left=sr
		sr.left=self
		# if sr.right is not None:
			# sr.right.parent=self
		sr.parent=self.parent
		self.parent=sr

	def rrot(self):
		sl=self.left
		if sl is None:
			return
		self.left=sl.right
		if sl.right is not None:
			sl.right.parent=self
		if self.parent is not None:
			if self.parent.left==self:
				self.parent.left=sl
			else:
				self.parent.right=sl
		sl.right=self
		sl.parent=self.parent
		self.parent=sl

	def bf(self):
		bf=Default(0,self.right).bind(SymTabNode.height).unwrap() - \
			Default(0,self.left ).bind(SymTabNode.height).unwrap()
		return bf
	#def __len__(self):
		#l=1
		#if self.left is not None:
			#l+=len(self.left)
		#if self.right is not None:
			#l+=len(self.right)
		#return l
	
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
	def height(self,frames=0) -> int:
		lh=0
		lh=Default(0,self.left).bind(SymTabNode.height)
		rh=Default(0,self.right).bind(SymTabNode.height)
		if frames > 30:
			pass
		return max(lh.unwrap(),rh.unwrap()) + 1 #pyright:ignore

	# NOTE: For debugging
	def lent(self,seed=0):
		l=1
		if seed > 10:
			pass
		if self.left is not None:
			l+=self.left.lent(seed+1)
		if self.right is not None:
			l+=self.right.lent(seed+1)
		return l
	def add_count(self,d:dict,rd=0) -> dict:
		if rd > 20:
			pass
		if self in d:
			d[self]+=1
		else:
			d[self]=1
		if self.left:
			d=self.left.add_count(d,rd+1)
		if self.right:
			d=self.right.add_count(d,rd+1)
		return d
	def print_to_graph(self):
		left=Maybe(self.left)
		if left:
			print(f"{self.contents} --> {left.contents}")
		right=Maybe(self.right)
		if right:
			print(f"{self.contents} --> {right.contents}")
		if self.parent:
			print(f"{self.contents} -- p --> {self.parent.contents}")
		left.bind(SymTabNode.print_to_graph)
		right.bind(SymTabNode.print_to_graph)


def get_stn_root(stn:SymTabNode):
	while stn.parent is not None:
		stn=stn.parent
	return stn
class SymTabNS:
	"""
	Holds and represents the namespace
	"""
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
			old_len=0
		else:
			old_len=self.root.lent()
			self.root.add(tk)
		self.root=get_stn_root(self.root)
		count_of_nodes=self.root.add_count(dict())
		if not all(map(lambda x:x==1, count_of_nodes.values())):
			print(f"Problem adding {tk.name}:")
			print("Not all tokens are unique! Repeated entries:")
			for k,v in count_of_nodes.items():
				if v != 1:
					print(f"\t {k} ({v})")
			return -1
		assert self.root.lent()==old_len+1,"We lost a node somewhere!"

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

class SymTab:
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
	def search(self,name:str,ns:list|None=None) -> str:
		if ns is None:
			ns=name.split('.')[:-1]
			name=name.split('.')[-1]
		if self.roots is None:
			raise MemoryError(f"You didn't initialize this parse tree yet!")
		ns_parent=trav_ns(self.roots,ns)
		result=ns_parent.root.get_tok(name)
		if result:
			return result.unwrap().val
		raise KeyError(f"No Token {name} exists in namespace {ns}!")
	def print(self):
		if self.roots is not None:
			self.roots.print()

