import json
import logging
import subprocess
import re
import util


def run_cmd(self, cmd, output=False, dry_run=False, logger=None):
	"""Runs a command using subprocess.
	dry_run just prints the command.
	If output is set, returns the output of the command.
	If output and dry_run are supplied, returns the value of output"""
	logger = logger or logging.getLogger()
	if dry_run:
		self.logger.info(" ".join(cmd))
		if output:
			return output
	else:
		if output:
			return subprocess.check_output(cmd)
		else:
			subprocess.call(cmd)


class Platform(object):
	#Won't be needed, slate for removal

	def __init__(self, args):
		self.dry_run = args.dry_run
		self.logger = util.configure_logger(__name__)

	def inplace_sed(regex, repl, dest):
		"""Uses a regex to replace something in a file.
		Tried to do this with `sed` command without success.
		This is more portable, and easier to reason about."""
		f = open(dest, 'r')
		data = f.read()
		rewritten = re.sub(regex, repl, data, re.MULTILINE)
		f.close()
		# some feedback here? We do do in place...
		#if args.dry_run:
			#print "rewriting {} with {}, {}".format(dest, regex, repl)
		#else:
		f = open(dest, 'w')
		f.write(rewritten)
		f.flush()
		f.close()


class Executable(object):
	"""General purpose class for running executables on command line"""
	pass


class Docker(Executable):

	binary = 'docker'

	def ensure_image(self, source_image):
		listing = self.run_cmd(['image', 'ls', source_image], output="HEADER\nimage-data\n")
		size = len(listing.split('\n'))
		if size <= 2:  # Empty listing is "HEADER\n", one newline split yields two rows
			return False
		return True


class Git(Executable):

	binary = 'git'

	def get_tag(self):
		branch = self.get_branch()
		_hash = self.get_short_hash()
		if not branch:
			raise ValueError("couldn't parse branch")
		if not re.match('^\w{6,10}$', _hash):
			raise ValueError("invalid tag from git: {}".format(_hash))
		return "{}-{}".format(branch, _hash)

	def get_short_hash(self):
		return self.run_cmd(['rev-parse', '--short', 'HEAD'], output='sometag\n').strip()

	def get_branch(self):
		return self.run(['rev-parse', '--abbrev-ref', 'HEAD'], output='current-branch').strip()


class Kube(Executable):

	binary = "kubectl"

	def __init__(self, namespace=None):
		self.namespace = namespace
		self.platform = Platform()

	def get_context(self):
		out = self.platform.run_cmd(self.make_cmd(
			['config', 'current-context'], never_namespace=True), output='current-cluster')
		return out

	def print_context(self):
		self.logger.info("running in {}".format(self.get_context()))

	def get_hostname_for_service(self, service_name):

		dns_cmd = self.make_cmd(["get", "-o", "json", "service", service_name])

		out = self.platform.run_cmd(dns_cmd, output={
			"status": {
				"loadBalancer": {
					"ingress": [
						{"hostname": "some.elb.dns.name.amazonaws.com"}]}}})
		service = json.loads(out)
		dns_target = service.get('status', {})\
				.get('loadBalancer', {})\
				.get('ingress', [{}])[0]\
				.get('hostname')

		return dns_target

	def make_cmd(self, cmd_array, never_namespace=False):
		if cmd_array[0] != Kube.binary:
			cmd_array = [Kube.binary] + cmd_array
		if self.namespace and not never_namespace:
			map(cmd_array.append, ["--namespace", self.namespace])

		return cmd_array
