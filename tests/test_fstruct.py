from unittest import TestCase
from spice_parser.fstruct import fstruct


class Testfstruct(TestCase):
	def setUp(self):
		self.path="epc2022_dpt.sp"
		self.fstruct=fstruct(self.path)
		self.fstruct.parse()

	def test_recenter(self):
		self.fstruct.recenter("test")
		assert self.fstruct.fullpath=="test/epc2022_dpt.sp"
		self.fstruct.recenter("test",suffix="_0")
		assert self.fstruct.fullpath=="test/epc2022_dpt_0.sp"
		sym=self.fstruct.get_st().search("epc")
		assert sym.val=='"EPC2022_hsp_0.lib"',str(sym.val)