import sys
sys.path.append('..')
from server import server, md_actions
server = server()






class login:
	"""Giveth JWT to the user"""
	def __init__(self):
		self.sex = 1


	def do_login(self):

		# construct the auth_hash
		# no partial matches allowed
		# auhash = server.util.eval_hash(server.prms['username'] + server.prms['pswd'], 'sha256')

		# get user info
		usr_info = server.wfauth.get_user_info(
			auth_hash=server.util.eval_hash(server.prms['username'] + server.prms['pswd'], 'sha256')
		)

		# in case of a success - a userid should be present
		# otherwise - deny
		# important todo: this is a very unreliable check
		if usr_info['userid'] == None:
			server.bin_jwrite({
				'status': 'error',
				'reason': 'invalid_credentials',
				'details': 'Unable to find a user with specified credentials'
			})
		else:
			user_details = server.authdb_path / 'authsys' / 'details' / usr_info['userid']
			server.bin_jwrite({
				'status': 'authorized',
				'is_admin': server.wfauth.is_admin,
				'jwt_token': server.wfauth.construct_token(server.jload(user_details / 'token.lzrd'))
			})

		server.flush()










login_class = login()

actions = md_actions(
	server,
	{
		'login': login_class.do_login
	}
)
actions.eval_action()