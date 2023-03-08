

class wafer_redundancy_journal:

	def __init__(self, rlist_path, wfutil, pathlib=None, json=None):
		import datetime
		self.datetime = datetime.datetime
		self.timedelta = datetime.timedelta

		# important todo: these two checks bring chaos, confusion and waste time 
		if not pathlib:
			from pathlib import Path
			pathlib = Path
		if not json:
			import json

		self.Path = pathlib
		self.json = json
		self.jdir = self.Path(rlist_path)
		self.wfutil = wfutil
		# self.srv = srv

	# takes the path to the file and the life length
	# life in hours
	# overwrites previous record, if any
	# important todo: choose whether to overwrite or no
	def reg_file(self, flpath, life=5):
		dtm = self.datetime
		tdelta = self.timedelta

		flpath = str(self.Path(flpath).as_posix()).strip('/')

		record = {
			'expiration_date': (dtm.now() + tdelta(hours=int(life))).isoformat(),
			'target': flpath,
		}

		record_id = self.wfutil.eval_hash(flpath, 'sha256')

		print(flpath, record_id)

		(self.jdir / f'{record_id}.jr').write_text(self.json.dumps(record))


	# manually remove a journal entry
	def unreg_file(self, flpath):
		unreg_id = self.wfutil.eval_hash(str(self.Path(flpath).as_posix()), 'sha256')
		print(flpath, unreg_id)
		(self.jdir / f'{unreg_id}.jr').unlink(missing_ok=True)




