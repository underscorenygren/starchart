import json
import time
from executables import AwsCli, run_cmd


class ImageRepository(object):

	"""Somewhat arbitrarily I only use dashes in remote docker images.
	But that makes them DNS safe, so we've stuck with this convention.
	There might be a case for making this configruable"""
	dashify = True

	def sanitize_and_tag(self, image_name, tag=None):
		dest_image = image_name
		tag = tag or 'latest'

		if self.dashify:
			dest_image = dest_image.replace('_', '-')

		if dest_image.find(':') == -1:
			dest_image = "{}:{}".format(dest_image, tag)

		return dest_image

	def tag_and_push(self, source_image, tag=None):

		dest_image = self.sanitize_and_tag(source_image, tag=tag)
		destination = self.get_full_destination(dest_image)
		self.docker.run_cmd(['tag', source_image, destination])
		self.do_push(destination)
		return destination


class ECR(ImageRepository):

	def __init__(self, repository_config={}):
		self.aws = AwsCli()
		self.image_region = repository_config['region']
		self.name = repository_config['name']

	def do_push(self, destination):
		self.docker.run_cmd(['push', destination])

	def login(self):

		login = self.aws.run_cmd(['ecr', 'get-login', '--no-include-email', '--region', self.image_region], output='login-info')
		logged_in = run_cmd(login.strip('\n').split(' '), output='success', dry_run=self.aws.dry_run)
		if logged_in.find("denied") == 0:
			return "couldn't log in to ecr with: {}".format(login)

	def get_destination(self, dest_image):
		return "{}/{}".format(self.name, dest_image)

	def clean_ecr(self, images, max_days_old):

		for image in images:
			image_data = self.aws.run_cmd(['ecr', 'describe-images', '--repository-name', image], output='{"imageDetails": [{"imageDigest": "somedigest", "imagePushedAt": 1308108}]}')
			images_json = json.loads(image_data)
			images = images_json['imageDetails']
			max_days = max_days_old
			to_delete = []
			for img in images:
				epoch = img['imagePushedAt']
				diff = time.time() - epoch
				if diff > (60 * 60 * 24 * max_days):
					to_delete.append('{}'.format(img['imageDigest']))

			print "deleting {} out of {}".format(len(to_delete), len(images))

			for digest in to_delete:
				self.aws.run_cmd(['ecr', 'batch-delete-image', '--repository-name', image, '--image-ids', 'imageDigest={}'.format(digest)])


class GCR(ImageRepository):

	def __init__(self, repository_config={}):
		self.name = repository_config['name']

	def login(self):
		"""No need for login"""
		return

	def get_destination(self, dest_image):
		return "{}/{}/{}".format('gcr.io', self.name, dest_image)

	def do_push(self, destination):
		self.gcloud.run_cmd(['docker', '--', 'push', destination])
