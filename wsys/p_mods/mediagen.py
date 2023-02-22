


# cfg is a dict where:
# {
# 	'thread_limit': 0 / 1 / 2 ...
# }
class media_gen:
	def __init__(self, cfg, task):
		self.cfg = cfg

		self.task = task

		actions = {
			'img': self.generate_pic_preview,
		}

		# Execute corresponding action
		actions[task]()

