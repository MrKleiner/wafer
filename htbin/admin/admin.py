#!/usr/bin/python3
import cgi, sys, cgitb
sys.path.append('.')
from server import server
server = server(cgi, sys, cgitb)


# this entire class requires admin
class user_ctrl:
	"""User control, like password control and account creation"""
	
	# init usually means auth
	def __init__(self, auth=None):
		if not server.alw_db.db.get(auth):
			server.bin_write(json.dumps({'status': '1809246/missing'}).encode())
			server.flush()

		if not 'admin' in server.alw_db.db[auth]:
			server.bin_write(json.dumps({'status': '1809246/hobo'}).encode())
			server.flush()


	# load users database
	# token is not passed intentionally
	def get_user_list(self):
		import json

		users = []

		for usr in server.auth_db.db:
			users.append({
				'login': usr,
				'pswd': user_db[usr]['pswd']
			})

		# return json.dumps(users)
		server.bin_write(json.dumps(users).encode())
		server.flush()


	# save users database
	# todo: keep a few backups of the databse, like .bend1, .blend2, blend3
	# important todo: for now this also responsible for creating new profiles...
	def save_user_profiles(self):
		from pathlib import Path
		import json

		# original database
		old_db_loc = auth_db.path
		old_db = auth_db.db

		# don't forget to update allowance db
		cldb_loc = alw_db.path
		cldb = alw_db.db

		# new users db
		new_db = {}
		# new allowance db
		new_cl_db = {}

		# eval input into json
		inp_db = json.loads(server.bin)

		# overwrite old db with new data
		for usr in inp_db:
			# if this user does not exist - create it
			if not old_db.get(usr):
				# important todo: this is absolutely fucking retarded
				# generate random access token
				super_token = self.generate_token()

				new_db[usr] = {
					'pswd': inp_db[usr],
					'token': super_token
				}

				# add token to clearance db
				new_cl_db[super_token] = {
					'admin': [],
					'folders': []
				}
			else:
				new_db[usr] = {
					'pswd': inp_db[usr],
					'token': old_db[usr]['token']
				}
				new_cl_db[old_db[usr]['token']] = cldb[old_db[usr]['token']]

		old_db_loc.write_bytes(json.dumps(new_db, indent=4).encode())
		cldb_loc.write_bytes(json.dumps(new_cl_db, indent=4).encode())

		server.bin_write(json.dumps({'status': 'ok', 'details': 're-wrote user databases'}).encode())
		server.flush()


	# generate random token
	def generate_token(self):
		import random
		return server.util.eval_hash('!lizard?'.join([str(random.random()) for rnd in range(64)]), 'sha256')



usr_ctrl = user_ctrl(server.prms.get('auth'))



if server.prms.get('action') == 'get_user_list':
	usr_ctrl.get_user_list()

