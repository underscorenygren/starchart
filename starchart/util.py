class AttrDict(dict):
	"""A convenience class for accessing dicts with dot notation"""
	def __init__(self, *args, **kwargs):
		super(AttrDict, self).__init__(*args, **kwargs)
		self.__dict__ = self

	def merge(self, new_dict):
		self.__dict__.update(new_dict)
		return self


class SafeAttrDict(AttrDict):
	"""An AttrDict that returns None instead of AttributeError"""

	def __getattr__(self, name):
		try:
			return super(AttrDict, self).__getattr__(self, name)
		except AttributeError:
			return None


def merge(a, b):
	"""Merges two dicts and returns result"""
	a.update(b)
	return a
