import inspect
import util


class CommandParser(object):

	DEFAULT_FN_NAME = 'default'

	def __init__(self, args):
		self.args = args

	@staticmethod
	def get_commands():
		return [(fn_name, fn) for (fn_name, fn) in
				inspect.getmembers(CommandParser, predicate=inspect.ismethod)
					if fn_name != CommandParser.DEFAULT_FN_NAME and fn_name[0] != '_']

	def test(self):
		"""A test"""
		print "test"

	def default(self):
		"""Displays the current starchart context"""
		print "default"


def make_subparser_fn(fn_name):
	"""Wrapped function that instantiate command parser with the calling args.
	Used so we can automatically wire parseable commands by adding methods
	to the CommandParser class without any other dependencies"""

	def call_with_args(args):
		runner = CommandParser(args)
		getattr(runner, fn_name)()

	return call_with_args


if __name__ == "__main__":

	import argparse
	import sys

	parser = argparse.ArgumentParser(description="Starchart, a kubernetes microservice framework")
	subparsers = parser.add_subparsers(help="What action to take. No action displays current context")

	for (fn_name, fn) in CommandParser.get_commands():
		subparser = subparsers.add_parser(fn_name, help=fn.__doc__)
		subparser.set_defaults(func=make_subparser_fn(fn_name))

	if len(sys.argv[1:]) == 0:
		# Because python2.7 argparse doesn't support optional subparsers, we have to hack this together
		# instead of specifying a default parser on the top level
		make_subparser_fn(CommandParser.DEFAULT_FN_NAME)(util.SafeAttrDict())
	else:
		args = parser.parse_args()
		args.func(args)
