from typing import Any, Callable, Generic, TypeVar

T=TypeVar('T')
class Maybe(Generic[T]):
   val:T
   valid:bool
   def __init__(self, val, valid=True):
      if isinstance(val,Maybe):
         self.val=val.val
         self.valid=val.valid
      else:
         self.val=val
         self.valid=valid
         if self.val is None:
            self.valid=False
   def __del__(self):
      if self.valid:
         del self.val
      del self
   def bind(self,f:Callable) -> 'Maybe':
      if self.valid:
         try:
            result = f(self.val)
            if result is not None:
               return Just(result)
         except Exception as e:
            return Empty()
      return Empty()
   def __bool__(self):
      return self.valid
   def __repr__(self):
      if self.valid:
         return str(Just(self))
      return str(Empty())
   def __getattr__(self,name):
      #if hasattr(self,name):
         #return self.__getattribute__(name)
      if hasattr(self.val,name):
         return getattr(self.val,name)
      raise AttributeError(f"{name} is not a valid attrribute!")
   def unwrap(self):
       if self.valid:
          return self.val
       return None

class Just(Maybe):
   def __init__(self, val):
      super().__init__(val, True)
   def __repr__(self):
      return f"Just {self.val}"

class Empty(Maybe):
   def __init__(self):
      super().__init__(None,False)
   def __repr__(self):
      return "Empty monad"
   def bind(self,f:Callable):
      return self

class Counter:
	val:int
	step:int
	rep:int
	def __init__(self,start_from=0,step=1,repeat=-1):
		self.val=start_from-step
		self.step=step
		self.rep=repeat
	def __call__(self):
		if self.rep > 0:
			self.val=(self.val+self.step)%self.rep
		else:
			self.val+=self.step
		return self.val
