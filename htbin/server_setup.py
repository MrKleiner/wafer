



# This script will set the server up before you can use it
# It's fine that this script is in the htbin directory,
# running it twice doesn't do anything and users cannot overload the system by randomly calling it
# (there are way more efficient and obvious ways of crashing/abusing/raping this poor system)







def run_setup():
	from pathlib import Path
	import json, sqlite3, shutil, datetime, base64
	from server_config import server_config
	from htcompile import compile_server
	import util

	serverdir = Path(__file__).parents[1]

	print('Running setup...')

	authdb_root = Path(server_config['authdb'])
	sysdb_root = Path(server_config['sysdb'])

	# First check if the databse exists already
	if (authdb_root / 'authsys' / 'users' / 'userdb.db').is_file():
		print('Databse is initialized already, if you want to reset it - read the instructions inside "factory_reset.py"')
		return

	# if it doesnt exist - proceed with creation n stuff


	#
	# check if all the specified paths exist
	#
	if not authdb_root.parent.is_dir():
		print('The parent of "authdb" does not exist')
		return

	if not sysdb_root.parent.is_dir():
		print('The parent of "sysdb" does not exist')
		return

	# now, actually do stuff...



	# first, wipe the contents of the target userdb directory
	if authdb_root.is_dir():
		shutil.rmtree(str(authdb_root))
	# and re-create the dir
	authdb_root.mkdir(exist_ok=True)
	(authdb_root / 'authsys').mkdir()
	syscfg = authdb_root / 'cfg'
	syscfg.mkdir()
	authdb_root = authdb_root / 'authsys'

	#
	# Create and initialize the user database
	#
	(authdb_root / 'users').mkdir()

	connection = sqlite3.connect(str(authdb_root / 'users' / 'userdb.db'))
	cursor_obj = connection.cursor()
	cursor_obj.execute("""
		CREATE TABLE authdb (
			user_id CHAR(64) NOT NULL UNIQUE,
			login VARCHAR NOT NULL UNIQUE,
			pswd VARCHAR NOT NULL,
			auth_hash CHAR(64) NOT NULL
		);
	""")






	# ===================================================
	#            CREATE A DEFAULT OWNER ACCOUNT
	# ===================================================
	owner_token = util.generate_token(True, 3)

	cursor_obj.execute(f"""
		INSERT INTO authdb
		(user_id, login, pswd, auth_hash)
		VALUES(
			"{owner_token}",
			"{base64.b64encode('owner'.encode()).decode()}",
			"{base64.b64encode('bagpipes'.encode()).decode()}",
			"{hashlib.sha256('owner'.encode() + 'bagpipes'.encode()).hexdigest()}"
		)
	""")


	#
	# Now create the details dir
	#
	(authdb_root / 'details').mkdir()

	# add owner
	(authdb_root / 'details' / owner_token).mkdir()
	# write owner stuff
	owner_info = {
		'created': datetime.datetime.now().isoformat(),
		'isadmin': True,
		'change_creds': True
	}
	(authdb_root / 'details' / owner_token / 'info.lzrd').write_bytes(json.dumps(owner_info))


	owner_token_file = {
		'userid': owner_token,
		'created': datetime.datetime.now().isoformat(),
		'crypto': util.generate_token(True, 5),
		'lifetime': 2_592_000_000
	}
	(authdb_root / 'details' / owner_token / 'token.lzrd').write_bytes(json.dumps(owner_token_file))


	owner_details = {
		'global': {},
		'target': {}
	}
	(authdb_root / 'details' / owner_token / 'rules.lzrd').write_bytes(json.dumps(owner_details))

	journal_file = {
		'last_login_ip': '',
		'last_login_time': ''
	}
	(authdb_root / 'details' / owner_token / 'journal.lzrd').write_bytes(json.dumps(journal_file))








	# ===================================================
	#            CREATE A DEFAULT EMPTY USER
	# ===================================================
	guest_token = util.generate_token(True, 3)

	cursor_obj.execute(f"""
		INSERT INTO authdb
		(user_id, login, pswd, auth_hash)
		VALUES(
			"{guest_token}",
			"{base64.b64encode('guest'.encode()).decode()}",
			"{base64.b64encode('1'.encode()).decode()}",
			"{hashlib.sha256('guest'.encode() + '1'.encode()).hexdigest()}"
		)
	""")


	#
	# Now create the details dir
	#
	(authdb_root / 'details').mkdir()

	# add owner
	(authdb_root / 'details' / guest_token).mkdir()
	# write owner stuff
	guest_info = {
		'created': datetime.datetime.now().isoformat(),
		'isadmin': False,
		'change_creds': False
	}
	(authdb_root / 'details' / guest_token / 'info.lzrd').write_bytes(json.dumps(guest_info))


	guest_token_file = {
		'userid': guest_token,
		'created': datetime.datetime.now().isoformat(),
		'crypto': util.generate_token(True, 1),
		'lifetime': 2_592_000_000
	}
	(authdb_root / 'details' / guest_token / 'token.lzrd').write_bytes(json.dumps(guest_token_file))


	guest_details = {
		'global': {},
		'target': {}
	}
	(authdb_root / 'details' / guest_token / 'rules.lzrd').write_bytes(json.dumps(guest_details))

	guest_journal_file = {
		'last_login_ip': '',
		'last_login_time': ''
	}
	(authdb_root / 'details' / guest_token / 'journal.lzrd').write_bytes(json.dumps(guest_journal_file))


	connection.commit()
	connection.close()

	(syscfg / 'default_user').write_bytes(guest_token.encode())





	#
	# create sysdb stuff
	#

	# wipe the contents of the target folder
	if sysdb_root.is_dir():
		shutil.rmtree(str(sysdb_root))
	# and re-create the dir
	sysdb_root.mkdir(exist_ok=True)
	# create required folders
	(sysdb_root / 'journal').mkdir()
	(sysdb_root / 'preview_queue').mkdir()
	(sysdb_root / 'temps').mkdir()



	#
	# Finally, compile the server
	#

	compile_server()




	print('Setup done')


















if __name__ == '__main__':
	run_setup()







