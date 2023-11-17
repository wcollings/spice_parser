from typing import Any, Callable, Generic, TypeVar

T=TypeVar('T')
class Maybe(Generic[T]):
	val:T
	valid:bool
	def __init__(self, val, valid=True):
		self.val=val
		self.valid=valid
	def __del__(self):
		if self.valid:
			del self.val
		del self
	def bind(self,f:Callable) -> 'Maybe':
		if self.valid:
			try:
				result = f(self.val)
				if result is not None:
					return Maybe(result)
			except Exception as e:
				return Empty()
		return Empty()
	def __bool__(self):
		return self.valid
	def __repr__(self):
		if self.valid:
			return str(self.val)
		return "...Empty monad"
	def __getattr__(self,name):
		if name in self.__dict__:
			return self.__dict__[name]
		if name in self.val.__dict__:
			return self.val.__dict__[name]


class Empty(Maybe):
	def __init__(self):
		super().__init__(None,False)
