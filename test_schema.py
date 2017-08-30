import unittest

from starchart.schema import Schema, Field


class TestSchema(unittest.TestCase):

	def assertNonEmpty(self, array, desired_len=None):
		if desired_len is None:
			self.assertNotEqual([], array)
			self.assertTrue(len(array) > 0)
		else:
			self.assertEqual(desired_len, len(array))

	def test_one_working_field(self):
		schema = Schema({"test": Field(int)})

		errors, parsed = schema.validate({"test": 1})
		self.assertEqual([], errors)
		self.assertEqual(parsed.test, 1)

	def test_one_broken_field(self):
		schema = Schema({"test": Field(int)})

		errors, parsed = schema.validate({"test": "la"})
		self.assertNonEmpty(errors)

	def test_working_and_broken(self):
		schema = Schema({"int": Field(int), "int2": Field(int)})

		errors, parsed = schema.validate({"int": 2, "int2": "str"})
		self.assertNonEmpty(errors)

	def test_conversion(self):
		schema = Schema({"test": Field(int)})
		errors, parsed = schema.validate({"test": "1"})
		self.assertEqual([], errors)
		self.assertEqual(parsed.test, 1)

	def test_not_required(self):
		schema = Schema({"test": Field(int, optional=True)})

		errors, parsed = schema.validate({"test": 1})
		self.assertEqual([], errors)
		self.assertEqual(parsed.test, 1)

		schema = Schema({"test_none": Field(int, optional=True)})
		errors, parsed = schema.validate({"test_none": None})
		self.assertEqual([], errors)
		self.assertEqual(parsed.test_none, None)

		schema = Schema({"test_empty": Field(int, optional=True)})
		errors, parsed = schema.validate({})
		self.assertEqual([], errors)
		self.assertEqual(parsed.test_empty, None)

	def test_nested(self):
		schema = Schema({
			"_name": Schema({
				"test": Field(int)
			})
		})

		errors, parsed = schema.validate({"some_name": {"test": 1}})
		self.assertEqual([], errors)
		self.assertEqual(parsed.some_name.name, "some_name")
		self.assertEqual(parsed.some_name.test, 1)

	def test_nested_errors(self):
		schema = Schema({
			"_name": Schema({
				"test": Field(int)
			})
		})

		errors, parsed = schema.validate({"some_name": {"test": "la"}})
		self.assertNonEmpty(errors)

	def test_two_nested(self):
		schema = Schema({
			"one": Schema({
				"test": Field(int)
			}),
			"two": Schema({
				"test": Field(str)
			})
		})

		test_dict = {
				"one": {
					"test": 1},
				"two": {
					"test": "la"}}

		errors, parsed = schema.validate(test_dict)
		self.assertEqual([], errors)
		self.assertEqual(parsed.one.test, 1)
		self.assertEqual(parsed.two.test, "la")

	def test_multiple_variable_assign(self):
		schema = Schema({
			"_name": Schema({
				"int": Field(int),
				"str": Field(str)
			})
		})

		test_dict = {
				"test1": {
					"int": 1,
					"str": "1"
				},
				"test2": {
					"int": 2,
					"str": "2"}}

		errors, parsed = schema.validate(test_dict)
		self.assertEqual([], errors)
		self.assertEqual(parsed.test1.int, 1)
		self.assertEqual(parsed.test1.str, "1")
		self.assertEqual(parsed.test2.int, 2)
		self.assertEqual(parsed.test2.str, "2")

	def test_deep_nesting(self):

		schema = Schema({
			"one": Schema({
				"_var": Schema({
					"two": Schema({
						"three": Field(int)})})})})
		test_dict = {
				"one": {
					"test": {
						"two": {
							"three": 3}}}}

		errors, parsed = schema.validate(test_dict)
		self.assertEqual([], errors)
		self.assertEqual(3, parsed.one.test.two.three)


if __name__ == "__main__":
	unittest.main()
