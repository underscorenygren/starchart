"""Stuff that I'm not sure we'll need anymore. Kept around for reference/inspiration for now"""

class GitRecord(Git):
	"""CaptainsLog?"""
	try:
		committed = run_cmd(['git', 'commit', '--no-verify', '-m', "deployed {images} @ {tag} on {cluster}".format(**{
				'images': ', '.join(args.image),
				'cluster': cluster,
				'tag': tag
			})], args, output="1 file changed, etcetc")
		if committed.find("no changes") != -1:
			raise Exception(err_msg)
	except subprocess.CalledProcessError:
		raise Exception(err_msg)

		run_cmd(['git', 'push'], args)
