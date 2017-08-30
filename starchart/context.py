import os


class Context(object):
	"""Maintains the state of the starchart in a home directory
	for the user."""

	CONTEXT_FILE_NAME = '.starchart.yaml'
	DEFAULT_CONTEXT_FILE = os.path.join(os.path.expanduser('~'), CONTEXT_FILE_NAME)

	def __init__(self):
		self.galaxy = None
		self.universe = None
		self.cluster = None

	def __dict__(self):
		return {
				"galaxy": self.galaxy,
				"universe": self.universe,
				"cluster": self.cluster}

	def get_clusters(self):

		if self.galaxy:
			return [Cluster.load_from_config(cluster_name) for cluster_name in self.config.galaxies]

		if self.cluster:
			return [Cluster.load_from_config(self.cluster)]

		return []

	def switch_galaxy(self, galaxy_name):
		if galaxy_name is None:
			self.logger.debug("unsetting galaxy")
		else:
			err = self.validate_galaxy(galaxy_name)
			if err:
				self.logger.error(err)
			else:
				self.galaxy = galaxy_name
				self.write_conf()

	def validate_galaxy(galaxy_name):
		pass

	def write_conf(self):
		fn = Context.CONTEXT_FILE
		try:
			with open(fn, 'w') as yaml_file:
				self.logger.debug("writing conf at {}".format(fn))
				yaml.dump(dict(self), yaml_file, default_flow_style=False)
		except IOError:
			self.logger.exception("You don't have permission to write to the config file at {}".format(fn))
