import yaml
from util import AttrDict


class SchemaOrField(object):
	def __init__(self, optional=False, default=None):
		self.optional = optional
		self.default = default

	def is_optional(self):
		return self.optional

	def keyify(self, parents, key=None):
		if key is not None:
			parents = parents + [key]
		return ".".join(parents)


class Schema(SchemaOrField):
	"""This is a general purpose class to allow enforcing of schemas
	from python dicts."""
	def __init__(self, schema_dict, **kwargs):
		SchemaOrField.__init__(self, **kwargs)
		self.schema_dict = schema_dict

	def __str__(self):
		return str({key: str(val) for (key, val) in self.schema_dict.items()})

	def get_missing_required_keys(self, _dict):
		required = [key for (key, schema_or_field) in self.schema_dict.iteritems() if not schema_or_field.is_optional]
		present_keys = _dict.keys()
		return [key for key in required if key not in present_keys]

	def get_variable_key(self, key):
		if key and key[0] == '_':
			return key[1:]
		return None

	def validate(self, value, parents=[]):
		# Schemas are recursively enforced
		failed = []
		succeeded = {}
		if isinstance(value, dict):
			_dict = value
			variables = [(self.get_variable_key(k), v) for (k, v) in self.schema_dict.items() if self.get_variable_key(k)]
			if variables and len(variables) != 1:
				err = "schema has mixed variable and fixed settings here {}".format(self.keyify(parents))
				return [err], None

			if variables:  # for variables, we iterate on each (key, value) in received dict
				variable_name, schema = variables[0]
				if not value.values():
					failed.append("{} missing dict for variable \"{}\" and schema {}".format(self.keyify(parents), variable_name, schema))

				for (key, subval) in value.iteritems():
					_failed, _succeeded = schema.validate(subval, parents + [key])
					for fail in _failed:
						failed.append(fail)
					if _succeeded:
						_succeeded[variable_name] = key
						succeeded[key] = _succeeded
			else:  # for non-variables, we enforce the sche
				for (key, schema_or_field) in self.schema_dict.iteritems():
					subval = _dict.get(key)
					if subval is not None:  # optional case is checked after
						try:
							_failed, _succeeded = schema_or_field.validate(subval, parents + [key])
							succeeded[key] = _succeeded
							for fail in _failed:
								failed.append(fail)
						except AttributeError:
							err_str = "value {} for key {} is not field or schema".format(schema_or_field, self.keyify(parents, key))
							return [err_str], None

			for missing_key, missing_schema in [(mk, ms) for (mk, ms) in self.schema_dict.items() if mk not in succeeded.keys()]:
				if missing_schema.is_optional():
					succeeded[missing_key] = missing_schema.default
				elif not self.get_variable_key(missing_key):  # variable keys handled above
					failed.append("required key {} missing".format(self.keyify(parents, missing_key)))

			return failed, AttrDict(succeeded)
		else:
			err_str = "key {} expected to be schema {} but is real value {}".format(self.keyify(parents), self, value)
			return [err_str], None


class Field(SchemaOrField):
	def __init__(self, field_type, **kwargs):
		SchemaOrField.__init__(self, **kwargs)
		self.field_type = field_type

	def __str__(self):
		return str(self.field_type)

	def validate(self, value, parents):
		validated = value if isinstance(value, self.field_type) else None
		if validated is None:
			try:  # supports validating int strings as ints for example
				validated = self.field_type(value)
			except ValueError:
				pass
			except TypeError:
				pass
		if validated is not None:
			return [], validated
		return ["{} value({}) doesn't match desired type({})".format(self.keyify(parents), value, self.field_type)], None


class SchemaParser(object):
	"""Validates schemas"""

	@staticmethod
	def from_yaml_file(path, schema):
		"""Validates a schema from a yaml file"""
		try:
			parsed = yaml.load(open(path, 'r'))
			return Schema(schema).validate(parsed)
		except IOError:
			return None, "No such file: {}".format(path)
		except yaml.YAMLError as ye:
			return None, "YAML file invalid: {}".format(str(ye))
