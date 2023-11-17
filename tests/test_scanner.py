from unittest import TestCase

from spice_parser import scanner
from spice_parser.stoken import EOFToken
import unittest


class ScannerTest(TestCase):
	def setUp(self) -> None:
		self.f = "epc_trimmed.sp"
		self.scanner = scanner.Scanner(self.f)



class TestScanner(TestCase):
	def setUp(self) -> None:
		self.f="epc2022_dpt.sp"
		self.scanner=scanner.Scanner(self.f)

	def test_get_next_token(self):
		r=self.scanner.get_next_token()
		r=self.scanner.get_next_token()
		long=self.scanner.get_next_token()
		assert ')' in long.val
		assert self.scanner.get_next_token().name==".param"

	def test_remove_lc_markers(self):
		f="epc_trimmer.sp"
		with open(f, 'r') as _file:
			lines = _file.read().splitlines(True)
			elems = sum([l.split(' ') for l in lines], [])
		ret = scanner.remove_lc_markers(elems[1:11])
		assert '' not in ret
		assert '+' not in ret

	def test_get_EOF(self):
		eof_found=False
		for tk in self.scanner:
			print(tk)
			tk_next=self.scanner.peek()
			if isinstance(tk_next, EOFToken):
				print("EOF Token found!")
				eof_found=True
		assert eof_found==True

	def test_len_of_line(self):
		scn=self.scanner
		scn.curr_idx=129
		tk=next(scn)
		tk=next(scn)
		self.assertEqual(scn.len_of_line(),3)
		scn=scanner.Scanner("device_models/EPC2022_hsp.lib")
		self.assertEqual(scn.len_of_line(),2)
