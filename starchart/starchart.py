#!/usr/local/bin/python

import argparse
import os
import yaml


def create_service(self, service_name, subdomain, upsert=False):

	(destination, target) = dns.create(service_name, subdomain, upsert=upsert)

	self.logger.info("found dns target, registered {} to {}".format(parse_destination(args), target))

	if not self.dry_run:
		dns.wait_for_connection(target, args.port)
		dns.wait_for_connection(destination, args.port)
	else:
		self.logger.info("skipping wait for dry run at {} and {}".format(target, destination))

	#TODO where does write_destinaitno live. Service object?
	self.logger.info("service is live at \n{}".format(dns.write_destination(destination, args.port)))


class Star(object):

	def validate_deploy_file(self):
		try:
			deploy_file_cont = open(deploy_file, 'r').read()
			try:
				yaml.load(deploy_file_cont)
				return None
			except yaml.YAMLError as ye:
				return "invalid yaml: {}".format(str(ye))
		except IOError:
			return "no deploy file: {}".format(deploy_file)


class Constellation(object):

	def __init__(self, path):
		self.error = None

		try:
			starchart = open(os.path.join(path, Starchart.FILE_NAME), 'r').read()
			self.starchart = yaml.load(starchart)
		except IOError:
			self.error = "no starchart.yaml found"
		except yaml.YAMLError as ye:
			self.error = "invalid yaml: {}".format(str(ye))

		self.composeable = any([os.path.isfile('docker-compose.{}'.format(ext)) for ext in 'yaml', 'yml'])
		self.dockerized = os.path.isfile(os.path.join(path, 'Dockerfile'))

	@staticmethod
	def load_from_cwd():
		return Constellation(os.getcwd())

	def validate(self):
		if self.error:
			return self.error

		if not self.composeable and not self.dockerized:
			return "no compose file or dockerfile detected"

	def build(self):
			build_cmd = None
			image_names = self.get_image_names()
			if self.composeable:
				build_cmd = self.docker_compose.build_command(image_names)
			elif self.is_dockerized():
				if len(image_names) != 0:
					return "Cannot build a dockerized deployment with more than one target - use docker-compose for that"
				build_cmd = docker.build_command(image_name[0])
			else:
				return "cannot build non-composeable, non-dockerized project"

			run_cmd(build_cmd)


def ignite(args):
	"""Creates a new set of microservices from the configs in the current directory"""

	binaries = Executable.load_all(args)

	pass


def deploy(args):

	constellation = Constellation.load_from_cwd()
	err = constellation.validate()
	if err:
		logger.error("Current directory isn't valid for starchart: {}".format(err))
		return

	# TODO multiple clusters into Galaxies
	cluster = get_current_cluster()
	if cluster.do_prompt():
		if raw_input("You are certain you want to deploy to {}? (y/n): ".format(cluster.name)).lower() != "y":
			logger.info("exiting in response to non-affirmative input")
			return

	targets = constellation.get_image_names()

	for image in targets:
		if not docker.ensure_image(source_image):
			logger.error("Source image {} not found in docker image list (did you use - instead of _ ?)".format(image))
			return

	err = constellation.build()
	if err:
		logger.error("build failure: {}".format(err))

	tag = git.get_tag()

	login_error = image_repo.login()
	if login_error:
		self.logger.error("couldn't log in to image repo: {}".format(login_error))

	for star in targets:

		image_repo = star.get_imager()
		destination = image_repo.tag_and_push(image_repo, tag=tag)

		if deploy_file:
			print "rewriting {dest} in deploy file {file}".format(**{'file': deploy_file, 'dest': destination})
			dest = destination
			tagless_img = dest[:dest.index(':')]

			regex = r"{}:\w+".format(tagless_img)

			inplace_sed(regex, dest, deploy_file, args)

	# TODO record deploy?

	kube.run_cmd(['replace', '-f', deploy_file])
	if wait_for_rollout:
		kube.wait_for_rollout(service_name)
