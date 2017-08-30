import json
import tempfile
import time
import util
import telnetlib


def test_connection(hostname, port):
	"""Tests that a connection is reachable using telnet"""
	t = telnetlib.Telnet()
	try:
		t.open(hostname, port)
		t.close()
		return None
	except Exception as e:
		return "couldn't connect to {}:{} - {}".format(hostname, port, e)


class Route53(object):

	# From here: https://forums.aws.amazon.com/thread.jspa?messageID=608949
	ELB_HOSTED_ZONE_IDS = util.AttrDict({
		"ap-northeast-1": "Z14GRHDCWA56QT",
		"ap-northeast-2": "ZWKZPGTI48KDX",
		"ap-south-1": "ZP97RAFLXTNZK",
		"ap-southeast-1": "Z1LMS91P8CMLE5",
		"ap-southeast-2": "Z1GM3OXH4ZPM65",
		"ca-central-1": "ZQSVJUPU6J1EY",
		"eu-central-1": "Z215JYRZR1TBD5",
		"eu-west-1": "Z32O12XQLNTSW2",
		"eu-west-2": "ZHURV8PSTC4K8",
		"us-east-1": "Z35SXDOTRQ7X7K",
		"us-east-2": "Z3AADJGX6KTTL2",
		"us-west-1": "Z368ELLRRE2KJ0",
		"us-west-2": "Z1H1FL5HABSF5",
		"sa-east-1": "Z2P70J7HTTTPLU",
	})
	KUBE_SLEEP_TIME_DEFAULT = 1
	TELNET_SLEEP_TIME_DEFAULT = 5

	def __init__(self, dry_run=False, config_data={}):
		self.dry_run = dry_run
		self.logger = util.configure_logger(__name__)
		hosted_zone_key = "hosted_zone"
		self.hosted_zone = config_data.get(hosted_zone_key)
		if not self.hosted_zone:
			raise ValueError("Configuration doesn't have hosted zone key: {}".format(hosted_zone_key))
		self.kube_sleep_time = config_data.get("kube_sleep_time", Route53.KUBE_SLEEP_TIME_DEFAULT)
		self.telnet_sleep_time = config_data.get("telnet_sleep_time", Route53.TELNET_SLEEP_TIME_DEFAULT)

	def create(self, service_name, subdomain, upsert=False):

		kube_name = service_name
		dns_target = None

		while not dns_target:
			dns_target = kube.get_hostname_from_service(service_name)
			if not dns_target:
				self.logger.info("waiting for kube service to become available")
				time.sleep(self.kube_sleep_time)

		destination = current_universe.make_subdomain(subdomain)
		region = cluster.region

		command = "CREATE" if not upsert else "UPSERT"
		jsonDoc = {
			"Comment": "changing service {} with {}".format(destination, command),
			"Changes": [{
				"Action": command,
				"ResourceRecordSet": {
					"Name": destination,
					"Type": "A",
					"AliasTarget": {
						"DNSName": dns_target,
						"EvaluateTargetHealth": False,
						"HostedZoneId": Route53.ELB_HOSTED_ZONE_IDS[region]}}}]}

		tmpfile = tempfile.NamedTemporaryFile(suffix=".json")
		tmpfile.write(json.dumps(jsonDoc))
		tmpfile.flush()

		route_cmd = ["aws", "route53", "change-resource-record-sets",
				"--hosted-zone-id", "/hostedzone/{}".format(self.hosted_zone),
				"--change-batch", "file://{}".format(tmpfile.name)]

		out = self.platform.run_cmd(route_cmd, output='route response')
		if self.dry_run:
			f = open(tmpfile.name, 'r')
			self.logger.info(f.read())
		self.logger.info(out)

		tmpfile.close()
		return [destination, dns_target]

	def wait_for_connection(self, hostname, port):
		while True:
			self.logger.debug("testing {}:{}".format(hostname, port))
			test_result = test_connection(hostname, port)
			if not test_result:
				break
			else:
				self.logger.debug(test_result)
				time.sleep(self.telnet_sleep_time)

	def write_destination(dest, port):
		if port == 80:
			return "http://{}".format(dest)
		elif port == 443:
			return "https://{}".format(dest)
		else:
			return "{}:{}".format(dest, port)
