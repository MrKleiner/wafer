


# ===============================================
#                Media queue
# ===============================================

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

		# Store reference to the main service controller
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


























# ===============================================
#                Redundancy Watcher
# ===============================================


def redundancy_watcher_loop(self):
	from pathlib import Path
	import time

	while True:
		# important todo: should this be configurable ?
		time.sleep(60*90)
		self.exec_scan()




# This is responsible for controlling the redundancy watcher
class wd_redundancy_watcher:
	def __init__(self, service):
		from pathlib import Path
		import threading, json
		from datetime import datetime

		self.datetime = datetime
		self.json = json

		# Store reference to the main service controller
		self.service = service
		# the directory containing journal records
		self.task_list_dir = Path(self.service.base_sys_cfg['sysdb']) / 'redundancy_list'

		# Currently processed item
		# In this case it's almost useless, but is good for detecting hangs
		self.current_item = None
		# the time taken by last traversal
		self.processing_time = None

		# self.is_scanning = False

		# launch the queue shit
		threading.Thread(target=redundancy_watcher_loop, args=(self,), daemon=True).start()


	# entry: pathlib.Path()
	def process_entry(self, entry):
		dtm = self.datetime
		rec_info = self.json.loads(entry.read_bytes())

		expires = dtm.fromisoformat(rec_info['expiration_date'])
		# todo: don't call this on each iteration?
		time_now = dtm.now()

		if time_now > expires:
			tgt_path = Path(rec_info['target'])
			# todo: directories are discarded for now
			if not tgt_path.is_dir():
				tgt_path.unlink(missing_ok=True)
			entry.unlink()

	# todo: bring it back to the main body of the loop ?
	# todo: also add a parameter to break out of the loop
	# and really, the iterator should be its own class threaded from the child thread
	# for better controls n shit...
	def exec_scan(self):
		import os

		op_start_time = time.time()

		# self.is_scanning = True

		for jrec in os.scandir(self.task_list_dir):
			try:
				jfile = Path(jrec.path)

				# useful for detecting whether the system is stuck or not
				self.current_item = jrec.name

				# making sure it's actually a journal record
				if not jfile.is_file() or not jfile.suffix.lower() == '.jr':
					# todo: better handling of this case
					continue

				# process the entry
				self.process_entry(jfile)

			except Exception as e:
				# todo: also try marking the journal file as broken
				self.service.wafer.syslog('rwatch_error', str(e))
				continue
		
		self.current_item = None
		# self.is_scanning = False

		# write down the amount of time it took to process the current list
		self.processing_time = time.time() - op_start_time



























# ===============================================
#              Main Watchdog Service
# ===============================================


# todo: use sqlite instead of file dumps?
# One advantage of file dumps is less likely to run into data corruption
class watchdogs_service:
	def __init__(self, cfgctrl, wafer=None):
		import datetime

		self.wcfg_ctrl = cfgctrl

		self.wafer = wafer

		# read configs on first start
		self.mgen_cfg = self.wcfg_ctrl['mediagen']
		# base system config
		self.base_sys_cfg = self.wcfg_ctrl['sysc_base']

		# init Lite
		self.qlite = wd_mqueue_ctrl(self, '.qi')

		# init Large
		self.qlarge = wd_mqueue_ctrl(self, '.qil')

		# init redundancy watcher
		self.rwatch = wd_redundancy_watcher(self)



	# reload configs from disk
	def reload_configs(self):
		# read configs on first start
		self.mgen_cfg = self.wcfg_ctrl['mediagen']
		# base system config
		self.base_sys_cfg = self.wcfg_ctrl['sysc_base']











