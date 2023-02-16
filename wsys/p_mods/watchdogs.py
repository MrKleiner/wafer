


def mqueue_loop(self):
	from pathlib import Path
	import time

	while True:
		time.sleep(60*5)




# This is responsible for controlling the media queue
class wd_mqueue_ctrl:
	def __init__(self, service, qtype):
		from pathlib import Path
		import threading

		# Store reference to the parent service controller
		self.service = service
		# Shortcut to the wafer config stored in the service
		self.wafer_cfg = self.service.wafer_cfg
		# The queue type ('.qi' / '.qil')
		self.qtype = qtype
		# The directory containing task files
		self.pqdir = Path(self.wafer_cfg['sysdb']) / 'preview_queue'

		self.current_item = None
		self.processing_time = None

		# launch the queue shit
		threading.Thread(target=mqueue_loop, args=(self,), daemon=True).start()




def redundancy_watcher_loop(self):
	from pathlib import Path
	import time

	while True:
		time.sleep(60*90)


# This is responsible for controlling the redundancy watcher
class wd_redundancy_watcher:
	def __init__(self, service):
		from pathlib import Path
		import threading

		# Store reference to the parent service controller
		self.service = service
		# Shortcut to the wafer config stored in the service
		self.wafer_cfg = self.service.wafer_cfg
		self.task_list_dir = Path(self.wafer_cfg['sysdb']) / 'redundancy_list'

		self.current_item = None
		self.processing_time = None

		# launch the queue shit
		threading.Thread(target=redundancy_watcher_loop, args=(self,), daemon=True).start()



# todo: use sqlite instead of file dumps?
# One advantage of file dumps is less likely to run into data corruption
class watchdogs_service:
	def __init__(self, srv_cfg):
		import datetime

		self.wafer_cfg = srv_cfg

		# init Lite
		self.qlite = wd_mqueue_ctrl(self, '.qi')

		# init Large
		self.qlarge = wd_mqueue_ctrl(self, '.qil')

		# init redundancy watcher
		self.rwatch = wd_redundancy_watcher(self)
















