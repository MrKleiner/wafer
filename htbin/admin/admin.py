import cgi, sys, cgitb
sys.path.append('..')
from server import server, md_actions
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
				'pswd': server.auth_db.db[usr]['pswd']
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


	# Load access definition list
	# Again, no tokens on purpose
	def load_access_list(self):
		import json

		# collapse token clearance and nicknames into a single dict
		clr_dict = {}

		clearance_db = server.alw_db.db
		user_db = server.auth_db.db

		for usr in user_db:
			clr_dict[usr] = clearance_db[user_db[usr]['token']]

		server.bin_write(json.dumps(clr_dict).encode())
		server.flush()



	# Save access list
	def save_access_list(self):
		from pathlib import Path
		import json

		# evaluate input as json
		input_cl = json.loads(server.bin)

		clearance_db = server.alw_db.db
		user_db = server.auth_db.db

		for usr in input_cl:
			clearance_db[user_db[usr]['token']]['folders'] = input_cl[usr]['folders']
			clearance_db[user_db[usr]['token']]['admin'] = input_cl[usr]['admin']

		server.alw_db.path.write_bytes(json.dumps(clearance_db).encode())

		server.bin_write(json.dumps({'status': 'ok', 'details': 're-wrote allowance db'}).encode())
		server.flush()




	# spawn struct with photos, videos n stuff
	def spawn_match_struct(self):
		import json

		sysroot = server.sys_root
		prms = server.prms

		# check whether the team exists or nah
		if not (sysroot / prms['team']).is_dir():
			server.bin_write(json.dumps({'status': 'fail', 'reason': 'requested team does not exist', 'details': str(sysroot / prms['team'])}).encode())
			server.flush()

		# now check for duplicate folders
		if (sysroot / prms['team'] / prms['newfld']).is_dir():
			server.bin_write(json.dumps({'status': 'fail', 'reason': 'duplicate names', 'details': str(sysroot / prms['team'] / prms['newfld'])}).encode())
			server.flush() 

		# finally, create the folder WITH subfolders n shit
		tgt_match = (sysroot / prms['team'] / prms['newfld'])
		tgt_match.mkdir()
		(tgt_match / 'video').mkdir()
		(tgt_match / 'photo').mkdir()
		(tgt_match / 'moments').mkdir()
		(tgt_match / 'pressa').mkdir()

		server.bin_write(json.dumps({'status': 'all_good'}).encode())
		server.flush()





usr_ctrl = user_ctrl(server.prms.get('auth'))

actions = md_actions(
	server, 
	{
		'get_user_list': 		usr_ctrl.get_user_list,
		'save_user_profiles': 	usr_ctrl.save_user_profiles,
		'load_access_list': 	usr_ctrl.load_access_list,
		'spawn_match_struct': 	usr_ctrl.spawn_match_struct,
		'save_access_list': 	usr_ctrl.save_access_list
	}
)
actions.eval_action()