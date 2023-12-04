from typing import Any, TypeVar

T=TypeVar('T')

def head(l:list[T]) -> T:
	return l[0]
def tail(l:list[T]) -> list[T]:
	return l[1:]
def reverse(l:list[T]) -> list[T]:
	return l[::-1]
def take(num:int, l:list[T]) -> list[T]:
	return l[:num]
def drop(num:int,l:list[T]) -> list[T]:
	return l[num:]

def list_lens(l:list[T],attr:str) -> list:
	"""
	Given a list of type, return a list of some specific attribute extracted from each element
	"""
	if len(l) > 1:
		return [getattr(head(l),attr)] + list_lens(tail(l),attr)
	elif len(l)==1:
		return [getattr(head(l),attr)]
	else:
		return []


