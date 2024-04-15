from os import path
from .stoken import CommentToken, SToken,EOLToken,EOFToken
from .linenumlist import LineNumList

lnl=LineNumList()
def insert(iter,fill):
	for elem in iter:
		yield elem
		yield fill
class Scanner:
	curr_idx=0
	line_no=0
	next_is_EOL:bool
	done:bool
	curr_line_start:int
	in_iter:bool
	def __init__(self,f):
		self.in_iter=False
		self.done=False
		self.fname=path.abspath(f)
		with open(f,'r') as _fp:
			lines=_fp.read().splitlines(False)
			tkBuff=[s.split(' ') for s in insert(lines,'\n')]
		self.tkBuff=[tk for tk in sum(tkBuff,[]) if tk!=""]
		self.next_is_EOL=False
		self.next_is_EOF=False
		self.curr_line_start=0
		self.done=False

	def reset(self):
		self.done=False
		self.next_is_EOF=False
		self.next_is_EOL=False
		self.curr_idx=0
		self.curr_line_start=0
		self.in_iter=False
	def __iter__(self):
		self.curr_idx=0
		self.line_no=0
		self.in_iter=True
		return self
	def __next__(self):
		if self.done:
			if self.in_iter:
				raise StopIteration
			else:
				return EOFToken()
		return self.get_next_token()

	def get_next_token(self):
		if self.curr_idx==len(self.tkBuff)-1:
			self.done=True
			return EOFToken(lnl.tail)
		if self.tkBuff[self.curr_idx]=='\n':
			if self.curr_idx == len(self.tkBuff)-1:
				self.done=True
				return EOFToken(lnl.tail)
			else:
				self.curr_idx+=1
				self.line_no+=1
				self.curr_line_start=self.curr_idx
				return EOLToken(lnl.tail)
		lnl.update(self.line_no)
		idx_delta=1
		res=self.tkBuff[self.curr_idx]
		first_line_comment=self.fname.split('.')[-1] in ['sp','in','net'] and self.line_no==0
		if res.startswith("*") or first_line_comment:
			idx_delta=find_next_occurance(self.tkBuff[self.curr_idx:],'\n')
			res=" ".join(self.tkBuff[self.curr_idx:self.curr_idx+idx_delta+1]).strip()
			self.line_no+=1
			self.curr_idx+=idx_delta
			return CommentToken(res,lnl.tail)
		elif '"' in res or "'" in res:
			quote_char={True:'"',False:"'"}['"' in res]
			idx_delta=find_next_occurance(self.tkBuff[self.curr_idx:],quote_char, ignore_first=True)
			ctx=remove_lc_markers(self.tkBuff[self.curr_idx:self.curr_idx+idx_delta+1])
			res=" ".join(ctx)
			self.curr_idx+=idx_delta+1
			idx_delta=0
		if self.curr_idx < len(self.tkBuff)-2 and self.tkBuff[self.curr_idx+2].startswith('+'):
			idx_delta+=2
		self.curr_idx+=idx_delta
		if "=" in res:
			strs=res.strip().split('=')
			var=strs[0]
			val='='.join(strs[1:])
		else:
			var=res.strip()
			val=""
		return SToken(var,val,lnl.tail)

	def peek(self) -> SToken:
		if self.next_is_EOF:
			return EOFToken(lnl.tail)
		if self.next_is_EOL:
			return EOLToken(lnl.tail)
		curr_idx=self.curr_idx
		eof=self.next_is_EOF
		eol=self.next_is_EOL
		ln=self.line_no
		tk=self.get_next_token()
		self.curr_idx=curr_idx
		self.line_no=ln
		self.next_is_EOF=False
		self.next_is_EOL=False
		return tk
	def len_of_line(self):
		idx_delta=find_next_occurance(self.tkBuff[self.curr_line_start:],'\n')
		return idx_delta



def find_next_occurance(arr, char: str,ignore_first:bool=False):
	i = 0
	fount_cnt=0
	for elem in arr:
		fount_cnt+=elem.count(char)
		if (fount_cnt==2 and ignore_first) or (fount_cnt==1 and not ignore_first):
			break
		i += 1
	return i


def remove_lc_markers(arr:list) ->list:
	true_list=[]
	nl=False
	for elem in arr:
		if nl==True or elem=='':
			nl=False
			continue
		if '\n' in elem:
			nl=True
			elem=elem.strip()
		true_list.append(elem)
	return true_list
