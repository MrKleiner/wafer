

# Finally a proper auth system





# auth is done on every request


class wfauth:
	"""Wafer auth system. Basically a bootleg version of proper auth systems"""
	def __init__(self, srv):
		self.srv = srv
		import base64
		self.b64 = base64
		from .access_resolver import resolver
		self.pth_auth = resolver

		# in the new system guests are strictly limited
		# and it's very important to know who's a guest and who's not
		self.guest = True
		self.isadmin = False

		# it's none by default as some actions do not require the path resolve
		# such as admin actions
		# (this saves a few milliseconds)
		self.user_rules = None

		# execute the auth process
		self.jwt_auth()




	def get_current_token(self):
		return self.construct_token()

	# collapse json into a token string
	def construct_token(self, tokenjson):
		token_result = ''

		token_result += tokenjson['userid']
		token_result += '.'
		token_result += self.b64.b64encode(tokenjson['created'].encode()).decode()
		token_result += '.'
		token_result += tokenjson['crypto']

		return token_result

	# generate new token for the user (overwriting the old one)
	def gen_token(self):
		import datetime
		# datetime.datetime.now().isoformat()
		# datetime.datetime.fromisoformat(sex)
		self.token['created'] = datetime.datetime.now().isoformat()
		# todo: use level 3 like before? (512 bits)
		self.token['crypto'] = self.srv.util.generate_token()
		# todo: dont forget to change this
		self.token['lifetime'] = 2_592_000_000

		(self.usr / 'token.lzrd').write_bytes(srv.json.dumps(self.token))

		return self.construct_token()

	# evaluate a path request
	def resolve_path(self, pth, wannawrite=False):
		if self.user_rules == None:
			self.user_rules = self.srv.jload(self.usr_path / 'rules.lzrd')

		decision = False
		for rule in self.user_rules['target']:
			decision = self.pth_auth(pth, rule, wannawrite)

		return decision

	# get full database record from userid
	# either by userid or auth_hash
	def get_user_info(self, userid=None, auth_hash=None):
		import sqlite3

		connection = sqlite3.connect(str(self.srv.authdb_path / 'authsys' / 'users' / 'userdb.db'))
		cursor_obj = connection.cursor()

		if auth_hash != None:
			cursor_obj.execute(f"""
				SELECT
					*
				FROM
					authdb
				WHERE
					auth_hash = "{auth_hash}";
			""")
		else:
			cursor_obj.execute(f"""
				SELECT
					*
				FROM
					authdb
				WHERE
					userid = "{userid}";
			""")

		infos = cursor_obj.fetchone()
		connection.close()

		if infos == None:
			return {
				'userid': None,
				'login': None,
				'pswd': None,
				'auth_hash': None
			}

		return {
			'userid': infos[0],
			'login': infos[1],
			'pswd': infos[2],
			'auth_hash': infos[3]
		}


	def request_admin(self):
		if not self.isadmin:
			self.srv.fatal_error('need_admin')
			self.srv.flush_json({'status': '1809246/hobo', 'details': 'Not enough privileges'})

	def reject_guest(self):
		if self.guest == True:
			self.srv.fatal_error('guest_disallowed')
			self.srv.flush_json({'status': '1809246/hobo', 'details': 'Guests are disallowed executing this action'})


	# allow using provided userid by validating the JWT
	# basically, a request comes with userID and a JWT token
	# and this function is responsible for validating that the provided userid can be used
	# theoretically, if crypto part of JWT is skipped, then anyone can access anyone's account by simply changing their userid
	def jwt_auth(self):
		provided_jwt = self.srv.headers.get('jwt')
		# if userid (and therefore the rest of jwt) is not present, then auth the request with a default user
		if provided_jwt == None:
			self.guest = True
			self.isadmin = False
			self.userid = (self.srv.authdb_path / 'authsys' / 'cfg' / 'default_user').read_text()
			details_path = self.srv.authdb_path / 'authsys' / 'details' / self.userid
			self.usr_path = details_path
			self.usr_info = self.srv.jload(details_path / 'info.lzrd')

			self.srv.set_header('wafer-guest', 'yes')
			return

		jwtsplit = provided_jwt.strip().split('.')

		# validate jwt structure
		# if invalid - reject the request completely,
		# since if token is present then it has to be a valid token
		if len(jwtsplit) != 3:
			self.srv.fatal_error('malformed_jwt')
			self.srv.flush_json({
				'error': 'malformed JWT token',
				'details': str(jwtsplit),
			})
			return

		# get token from authsys and check if it matches the provided one
		userid = jwtsplit[0]

		# get user info, if any
		# userinfo = self.get_user_info(self.userid)
		details_path = self.srv.authdb_path / 'authsys' / 'details' / userid

		# if no user was found under specified id - reject the request
		if not details_path.is_dir():
			self.srv.fatal_error('invalid_userid')
			self.srv.flush_json({
				'error': 'invalid_userid',
				'details': 'User with the specified ID does not exist',
			})
			return

		# now validate the JWT token
		jwt_from_db = self.construct_token(self.srv.jload(details_path / 'token.lzrd'))

		if jwt_from_db != provided_jwt:
			self.srv.set_header('wafer-error', 'invalid_jwt')
			self.srv.flush(self.srv.json.dumps({
				'error': 'invalid_jwt',
				'details': 'The provided token does not match the user token from db'
			}).encode())
			return

		# if validation went fine, then set system variables for further actions
		self.guest = False
		self.userid = userid
		self.usr_path = details_path
		self.usr_info = self.srv.jload(details_path / 'info.lzrd')
		self.isadmin = self.usr_info['isadmin']

		self.srv.set_header('wafer-admin', self.isadmin)

		return True
