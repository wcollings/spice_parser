from unittest import TestCase
from spice_parser import Parser
from spice_parser.stoken import SToken


class TestParser(TestCase):
	def setUp(self):
		parser = Parser("epc2022_dpt.sp")
		parser.parse()
		self.parser=parser
	def test_new_objects(self):
		parser = Parser("epc2022_dpt.sp")
		parser.parse()
		parser.write_all()
		del parser
		parser = Parser("epc2022_dpt.sp")
		parser.parse()
		parser.write_all()
		print(parser.get_all_files())
		assert len(parser.get_all_files())==3
		parser = Parser("epc2022_dpt.sp")
		parser.parse()
		parser.write_all()
		# print(parser.get_all_files())
		assert len(parser.get_all_files())==3

	def test_get_symbol(self):
		# assert SToken("asd1","") in self.parser.get_symtab().root.unwrap()
		res=self.parser.get_symbol("epc.EPC2022.asd1")
		assert res is not None
		res = self.parser.get_symbol("L0_A")
		assert res is not None
