#!/usr/bin/python3
import cgi, sys, cgitb
sys.path.append('.')
from server import server
server = server(cgi, sys, cgitb)

# basic stuff like login
class profiling:
	def __init__(self):
		self.ff = 'nen'

	# get login token
	def login(self):
		import json

		# evaluate server database
		authdb = server.auth_db.db

		username_fromdb = authdb.get(prms['username'])

		# check if username exists
		if username_fromdb:
			pswd_fromdb = authdb[prms['username']]['pswd']

			# if received pswd and db pswd match - return token
			if pswd_fromdb == prms['password']:
				server.bin_write(json.dumps({'status': 'success', 'token': authdb[prms['username']]['token']}).encode())
				server.flush()
			else:
				server.bin_write(json.dumps({'status': '1809246/p'}).encode())
				server.flush()
		else:
			server.bin_write(json.dumps({'status': '1809246/u/'}).encode())
			server.flush()


profiler = user_ctrl(server.prms.get('auth'))



if url_params.get('action') == 'login':
	profiling.login()



