from .monad import Maybe, Empty

class LineNumNode:
	"""
	Holds the current line number that the file being read is at
	"""
	next:'Maybe[LineNumNode]'
	lineNum:int
	def __init__(self, ln) -> None:
		self.lineNum=ln
		self.next=Empty()
	def __repr__(self):
		return str(self.lineNum)

class LineNumList:
	"""
	Wrapper class for `LineNumNode`
	"""
	head:LineNumNode
	tail:LineNumNode
	def __init__(self) -> None:
		self.head=self.tail=LineNumNode(0)

	def update(self, ln):
		if self.tail.lineNum==ln:
			return
		self.tail.next=Maybe(LineNumNode(ln))
		self.tail = self.tail.next.val
	
	def __del__(self):
		head=Maybe(self.head)
		while head:
			last=head
			head=head.val.next
			del last
