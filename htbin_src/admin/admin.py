import sys
sys.path.append('..')
from server import server, jateway
server = server()

# reject non-admin users immediately
server.wfauth.require_admin()

# codes:
# 1809246
# 2446
# 314
# 10092007



# this entire class requires admin
class user_ctrl:
	"""User control, like password control and account creation"""

	# init usually means auth
	def __init__(self):
		self.usr_dbfile = server.authdb_path / 'authsys' / 'users' / 'userdb.db'


	# load users database
	# important todo: decode login/pswd on the server or on the client ?
	# for now, decode on the client
	def get_user_list(self):
		import sqlite3

		users = []

		# get user IDs, logins and passwords
		connection = sqlite3.connect(str(self.usr_dbfile))
		cursor_obj = connection.cursor()
		cursor_obj.execute("""
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
			} | server.jload(server.authdb_path / 'authsys' / 'details' / usr[0] / 'info.lzrd')
			)

		server.bin_jwrite(users)
		server.flush()

	

	def update_users(self):
		pass







usr_ctrl = user_ctrl()

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
# actions.eval_action()