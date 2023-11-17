from unittest import TestCase
from spice_parser import Parser


class TestParser(TestCase):
	def setUp(self):
		pass
	def test_new_objects(self):
		parser = Parser("epc2022_dpt.sp")
		parser.parse()
		parser.write_all()
		del parser
		parser = Parser("epc2022_dpt.sp")
		parser.parse()
		parser.write_all()
		print(parser.get_all_files())
		assert len(parser.get_all_files())==2
		parser = Parser("epc2022_dpt.sp")
		parser.parse()
		parser.write_all()
		print(parser.get_all_files())
		assert len(parser.get_all_files())==2


	def test_get_all_files(self):
		self.fail()

	def test_parse(self):
		self.fail()

	def test_write_all(self):
		self.fail()

	def test_replace_val(self):
		self.fail()
