import sys
sys.path.append('..')
from server import server, md_actions
from gen import media_gen
server = server()



# Basically, there are two queues:
# large and lite
# large is responsible for processing large files, like vidoes
# and lite is responsible for processing small files, like images
class media_q:
	"""
	This is responsible for any media generation possible
	Large files are prefixed with .qi (queue item) and small files, like images are prefixed with .qil (queue item lite)
	applicable task types are: large | lite
	"""
	def __init__(self, task_type='large'):
		self.srv = server

		self.task_type = task_type

		self.lock_names = {
			'large': 'wafer_mq_running.large.wafer',
			'lite': 'wafer_mq_running.lite.wafer'
		}

		self.lock_name = self.lock_names[task_type]

		# try starting the processing
		self.launch()


	def launch(self):
		from pathlib import Path
		import os
		# if the queue is running already - don't do shit
		lock = (self.srv.sysdb_path / 'preview_queue' / self.lock_name)
		if lock.is_file():
			return

		# else - start processing
		

		# create the lock file
		# which contains pid of the current process
		lock.write_text(str(os.getpid()))

		# path to the folder containing preview journal records 
		task_pool = self.srv.sysdb_path / 'preview_queue'

		task_types = {
			'large': '.qi',
			'lite': '.qil'
		}

		# keep going trough the items in the queue
		# every item is a json dict where:
		# input: absolute file path to the target item
		# output: absolute path to the destination file
		# task: what to do with the given file
		# 	valid entries are: webm/frame_preview
		# webm stands for DASH shite
		while True:
			# get a queue entry
			# gather tasks from the task pool
			all_items = [itp for itp in task_pool.glob(f'*{task_types[self.task_type]}')]
			# if the list is empty - it means that there's nothing to do
			if len(all_items) <= 0:
				break

			# if there's at least one entry - get it
			# actually, get the last one
			# because getting the first one may result in the older entries never being reached
			# todo: wait, does this logic make any sense?
			current_item = all_items[-1]

			# evaluate the task
			task_info = json.loads(current_item.read_bytes())
			inp_loc = Path(str(task_info['input']))

			# don't do shit if input or output is invalid
			# todo: for now there's only input
			# if not inp_loc.is_file() or not inp_loc.parent.is_dir():
			if not inp_loc.is_file():
				# self.errlog_manual(f'file: {str(current_item)}, error: input or output destination does not exist')
				# indicate that this file is broken
				os.rename(str(current_item), str(current_item.with_suffix('.broken')))
				continue

			# first of all - extend the lock lifetime

			# todo: the lock file is literally the thing which keeps 70% of the system together
			# if something goes wrong with the lock file mechanism - everything is fucked
			# fj.reg_file(q_lock_file, 12)
			# fj.process_jr()

			# do what was asked
			# important todo: It's an assumption that all functions take exactly one parameter
			# and that this parameter is the task description
			# media_gen.actions[task_info['task']](task_info)
			generator = media_gen(self.srv, task_info)

			# once done with the action - delete the task file
			current_item.unlink(missing_ok=True)


		# once done with the queue - remove the lock file
		lock.unlink(missing_ok=True)

		self.srv.flush('kill linux'.encode())


	# this will kill any previously running queues and launch a new one
	def restart(self):
		import os

		lock = (self.srv.sysdb_path / 'preview_queue' / self.lock_name)

		if lock.is_file():
			# kill the running process by pid
			# important todo: what if this pid is assigned to another process?
			os.kill(int(lock.read_text()), signal.SIGTERM)
			# and remove the lock file
			lock.unlink()

		# launch new
		self.launch()




