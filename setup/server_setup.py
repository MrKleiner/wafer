from pathlib import Path
import json, sqlite3, shutil, datetime, base64, hashlib, cgi, sys, os, socket, py_compile
import subprocess as sp
# from server_config import server_config
# from htcompile import compile_server
# import util

server = Path(__file__).absolute().parent.parent
thisdir = Path(__file__).absolute().parent


# The sane maximum size of a file stored within the system is about 24gb
# Please use torrents for anything above this number


# Fast setup guide:
# install ffmpeg and image magick
# edit server_config.py
# Run this file (server_setup.py) from the user which would later run the lightppd process
# Setup lighttpd (apt install lighttpd)
# Create lighttpd config which points to the directory with index.html as server root (parent of this dir)
# Configure lighttpd the way that all .py files inside htbin are executed with the latest python version (3.8+)
# Enable x-sendfile in the said lighttpd config
# Launch lighttpd
# enjoy






# This script will set the server up before you can use it
# It's fine that this script is in the htbin directory,
# running it twice doesn't do anything and users cannot overload the system by randomly calling it
# (there are way more efficient and obvious ways of crashing/abusing/raping this poor system)






def run_setup(server_config):


	serverdir = Path(__file__).absolute().parents[1]

	print('Running setup...')

	authdb_root = Path(server_config['authdb'])
	sysdb_root = Path(server_config['sysdb'])

	# First check if the databse exists already
	if (authdb_root / 'authsys' / 'users' / 'userdb.db').is_file():
		print('Databse is initialized already, if you wish to reset it - read the instructions inside "factory_reset.py"')
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
	authdb_root = authdb_root / 'authsys'
	syscfg = authdb_root / 'cfg'
	syscfg.mkdir()



	#
	# Create and initialize the uploads log
	#
	connection = sqlite3.connect(str(authdb_root / 'users' / 'uploads.db'))
	cursor_obj = connection.cursor()
	cursor_obj.execute("""
		CREATE TABLE uploads (
			user_id CHAR(64) NOT NULL UNIQUE,
			dest VARCHAR NOT NULL,
			init_time TIMESTAMP,
			end_time TIMESTAMP,
			token CHAR(64) NOT NULL UNIQUE,
			duration INT,
			declared_hash CHAR(64) NOT NULL,
			result_hash CHAR(64),
			size BIGINT
		);
	""")
	connection.commit()
	connection.close()



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

	#
	# Now create the details dir
	#
	(authdb_root / 'details').mkdir()




	# ===================================================
	#            CREATE A DEFAULT OWNER ACCOUNT
	# ===================================================
	owner_token = util.generate_token(False, 3)

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


	# add owner
	(authdb_root / 'details' / owner_token).mkdir()
	# write owner stuff
	owner_info = {
		'created': datetime.datetime.now().isoformat(),
		'isadmin': True,
		'change_creds': True
	}
	(authdb_root / 'details' / owner_token / 'info.lzrd').write_bytes(json.dumps(owner_info).encode())


	owner_token_file = {
		'userid': owner_token,
		'created': datetime.datetime.now().isoformat(),
		'crypto': util.generate_token(False, 5),
		'lifetime': 2_592_000_000
	}
	(authdb_root / 'details' / owner_token / 'token.lzrd').write_bytes(json.dumps(owner_token_file).encode())


	owner_details = {
		'global': [],
		'target': []
	}
	(authdb_root / 'details' / owner_token / 'rules.lzrd').write_bytes(json.dumps(owner_details).encode())

	journal_file = {
		'last_login_ip': '',
		'last_login_time': ''
	}
	(authdb_root / 'details' / owner_token / 'journal.lzrd').write_bytes(json.dumps(journal_file).encode())








	# ===================================================
	#            CREATE A DEFAULT EMPTY USER
	# ===================================================
	guest_token = util.generate_token(False, 3)

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


	# add owner
	(authdb_root / 'details' / guest_token).mkdir()
	# write owner stuff
	guest_info = {
		'created': datetime.datetime.now().isoformat(),
		'isadmin': False,
		'change_creds': False
	}
	(authdb_root / 'details' / guest_token / 'info.lzrd').write_bytes(json.dumps(guest_info).encode())


	guest_token_file = {
		'userid': guest_token,
		'created': datetime.datetime.now().isoformat(),
		'crypto': util.generate_token(False, 1),
		'lifetime': 2_592_000_000
	}
	(authdb_root / 'details' / guest_token / 'token.lzrd').write_bytes(json.dumps(guest_token_file).encode())


	guest_details = {
		'global': [],
		'target': []
	}
	(authdb_root / 'details' / guest_token / 'rules.lzrd').write_bytes(json.dumps(guest_details).encode())

	guest_journal_file = {
		'last_login_ip': '',
		'last_login_time': ''
	}
	(authdb_root / 'details' / guest_token / 'journal.lzrd').write_bytes(json.dumps(guest_journal_file).encode())


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
	(sysdb_root / 'previews').mkdir()
	(sysdb_root / 'cgi_err').mkdir()
	(sysdb_root / 'uploads').mkdir()
	(sysdb_root / 'temps').mkdir()



	#
	# Finally, compile the server
	#

	compile_server()




	print('Setup done')





if __name__ == '__main__':
	incoming_info = json.loads(sys.stdin.buffer.read())

	sv_conf = {
		'system_root':         incoming_info['ftp_root'],
		'ffmpeg':              incoming_info['ffmpeg_path'],
		'ffprobe':             incoming_info['ffprobe_path'],
		'magix':               incoming_info['magix_path'],
		'authdb':              incoming_info['authdb_path'],
		'sysdb':               incoming_info['sysdb_path'],
		'watchdogs_port':      incoming_info['watchdog_port'],
		'upload_service_port': incoming_info['upload_service_port'],
	}

	conf_buffer = 'server_config = {'
	for txtbased in ('system_root','ffmpeg','ffprobe','magix','authdb','sysdb',):
		conf_buffer += f"""{txtbased} = '{sv_conf[txtbased]}'""" + '\n'

	conf_buffer += f"""watchdogs_port = {sv_conf['watchdogs_port']}""" + '\n'
	conf_buffer += f"""upload_service_port = {sv_conf['watchdogs_port']}""" + '\n'
	conf_buffer += '}'

	src_config_py = thisdir / 'server_cfg.py'
	src_config_py.write_text(sv_conf)

	py_compile.compile(str(src_config_py), cfile='server_config.pyc')
	src_config_py.unlink()
	shutil.copy(src_config_py.with_suffix('.pyc'), server / 'htbin' / 'server_config.pyc')

	print('Content-Type: application/octet-stream\r\n\r\n')
	# print('fuckoff')
	run_setup(sv_conf)





