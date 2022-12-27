import sys
sys.path.append('..')
from server import server, md_actions
server = server()

# classified info:

# reject reasons:
# 1809246: bad auth
# 1809246/nen: missing params

# 2446: invalid auth username
# 314: invalid auth password

# 10092007: requested upload lfs target does not exist


# this entire class requires admin
class user_ctrl:
	"""User control, like password control and account creation"""

	# init usually means auth
	def __init__(self, auth=None):
		if not server.wfauth.isadmin:
			server.bin_jwrite({'status': '1809246/hobo'})
			server.flush()


	# load users database
	# token is not passed intentionally
	# important todo: decode login/pswd on the server or on the client ?
	# for now, decode on the client
	def get_user_list(self):
		import sqlite3

		users = []

		# get user IDs, logins and passwords
		connection = sqlite3.connect(str(server.authdb_path / 'authsys' / 'users' / 'userdb.db'))
		cursor_obj = connection.cursor()
		cursor_obj.execute(f"""
			SELECT
				user_id, login, pswd
			FROM
				authdb
		""")
		user_creds = cursor_obj.fetchall()
		connection.close()

		# for every user write down his login creds and read user info from disk
		for usr in user_creds:
			users.append({
				'userid': usr[0],
				'login': usr[1],
				'pswd': usr[2],
				'rules': server.jload(server.authdb_path / 'authsys' / 'details' / usr[0] / 'rules.lzrd')
			})

		server.bin_jwrite(users)
		server.flush()


	# save users database
	# todo: keep a few backups of the databse, like .bend1, .blend2, blend3
	# important todo: for now this also responsible for creating new profiles...
	def save_user_profiles(self):
		from pathlib import Path
		import json

		# original database
		old_db_loc = server.auth_db.path
		old_db = server.auth_db.db

		# don't forget to update allowance db
		cldb_loc = server.alw_db.path
		cldb = server.alw_db.db

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
				super_token = server.util.generate_token()

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

		server.bin_jwrite({'status': 'ok', 'details': 're-wrote user databases'})
		server.flush()

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

		server.bin_jwrite(clr_dict)
		server.flush()



	# Save access definition list
	def save_access_list(self):
		from pathlib import Path
		import json

		# evaluate input as json
		input_cl = json.loads(server.bin)

		# new_clr_dict = {}

		cl_db_path = server.alw_db.path
		clearance_db = server.alw_db.db
		user_db = server.auth_db.db

		for usr in input_cl:
			clearance_db[user_db[usr]['token']]['folders'] = input_cl[usr]['folders']
			clearance_db[user_db[usr]['token']]['admin'] = input_cl[usr]['admin']

		cl_db_path.write_bytes(json.dumps(clearance_db).encode())

		server.flush('Saved allowance pool'.encode())




# this entire class requires admin
class struct_ctrl:
	"""File struct control, like spawning new folders"""

	def __init__(self):

		self.aa = 'bb'


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
		(tgt_match / 'photosession').mkdir()

		server.bin_write(json.dumps({'status': 'all_good'}).encode())
		server.flush()





usr_ctrl = user_ctrl(server.prms.get('auth'))
# this is very risky
# make auth check a separate class
file_ctrl = struct_ctrl()

actions = md_actions(
	server, 
	{
		# user control
		'get_user_list': 		usr_ctrl.get_user_list,
		'save_user_profiles': 	usr_ctrl.save_user_profiles,
		'load_access_list': 	usr_ctrl.load_access_list,
		'save_access_list': 	usr_ctrl.save_access_list,
		# File struct control
		'spawn_match_struct': 	file_ctrl.spawn_match_struct
	}
)
actions.eval_action()