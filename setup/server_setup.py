from pathlib import Path
import json, sqlite3, shutil, datetime, base64, hashlib, cgi, sys, os, py_compile
import subprocess as sp


server = Path(__file__).absolute().parents[1]
wsys_root = server.parent
thisdir = Path(__file__).absolute().parent

sys.path.append(str(server.parent / 'wsys' / 'p_mods'))
sys.path.append(str(server))

import htbin_src.wafer_util as wfutil
from json_compile import compile_json
from dir2pyc import dir2pyc
# The sane maximum size of a file stored within the system is about 24gb
# Please use torrents for anything above this number

class db_connect:
	def __init__(self, dbpath):
		self.connection = sqlite3.connect(str(dbpath))
		self.cursor_obj = connection.cursor()

		self.exec = self.cursor_obj.execute
		self.commit = self.connection.commit
		self.close = self.connection.close

	def iexec(self, *args):
		self.cursor_obj.execute(*args)
		self.connection.commit()

	def iexec_many(self, *args):
		self.cursor_obj.executemany(*args)
		self.connection.commit()


def b64str(s):
	return base64.b64encode(s.encode()).decode()



class srv_setup:
	def __init__(self, server_config, wipecfg=False):
		self.cfg = server_config

		self.init_authdb(wipecfg)
		self.init_sysdb(wipecfg)

		# Compile htbin to pyc
		dir2pyc(server / 'htbin_src', server / 'htbin')

		# Compile rapid access config
		# todo: is there a better way in python to do this ?
		# important todo: split the into into lines for faster evaluation
		compile_json(
			{
				'authdb':              str(self.cfg['authdb']),
				'sysdb':               str(self.cfg['sysdb']),
				'xfiles':              str(self.cfg['xfiles']),
				'watchdogs_port':      str(self.cfg['watchdogs_port']),
				'upload_service_port': str(self.cfg['upload_service_port']),
			},
			server / 'htbin' / 'server_config.json'
		)

		# write other configs
		(wsys_root / 'wsys' / 'sysc' / 'sysc_base.lzrd').write_text(json.dumps({
			'ftproot':             self.cfg['ftp_root'],
			'ffmpeg':              self.cfg['ffmpeg'],
			'ffprobe':             self.cfg['ffprobe'],
			'magix':               self.cfg['magix'],
			'authdb':              self.cfg['authdb'],
			'sysdb':               self.cfg['sysdb'],
			'xfiles':              self.cfg['xfiles'],
			'watchdogs_port':      self.cfg['watchdogs_port'],
			'upload_service_port': self.cfg['upload_service_port'],
			'upload_size_limit':   (1024**2)*80_000,
			'upload_timeout':      24,
		}, indent='\t'))

		(wsys_root / 'wsys' / 'sysc' / 'mediagen.lzrd').write_text(json.dumps({
			'limit_threads': 2,
			'picgen': {
				'size': 1,
				'quality': 1,
			},
			'vidgen': {
				'quality': 1,
			},
		}, indent='\t'))


		# and change permissions
		# important todo: this is obviously a pretty bad way of achieving it
		for cm in (server / 'htbin').rglob('*.pyc'):
			os.chmod(str(cm), 0o555)

		for cm in (server / 'apis').rglob('*'):
			os.chmod(str(cm), 0o444)





	def dir_condition(self, dir, wipe):
		dir = Path(dir)
		if dir.is_dir():
			if wipe:
				shutil.rmtree(dir)
			else:
				return True
		dir.mkdir(exist_ok=True)

	# {
	# 	'login': '',
	# 	'pswd': '',
	# 	'isadmin': False,
	# 	'edit_self': False,
	# 	'server_render': False,
	# 	'torrenting': False,
	# 	'edit_thumbs': False,
	# }
	def create_user(self, usrcfg):

		user_db = db_connect(Path(self.cfg['authdb_path']) / 'authsys' / 'users' / 'userdb.db')

		usr_id = wfutil.generate_token()

		# create db record
		user_db.iexec(
			"""
				INSERT INTO authdb
				(user_id, login, pswd, auth_hash)
				VALUES (?, ?, ?, ?);
			""",
			(
				usr_id,
				b64str(usrcfg['login']),
				b64str(usrcfg['pswd']),
				hashlib.sha256(f"""{usrcfg['login']}{usrcfg['pswd']}""".encode()).hexdigest(),
			)
		)
		user_db.close()

		# Fill details
		details = Path(self.cfg['authdb_path']) / 'authsys' / 'details' / usr_id
		details.mkdir()

		(details / 'info.lzrd').write_text(
			json.dumps({
				'created':       datetime.datetime.now().isoformat(),
				'login':         usrcfg['login'],
				'isadmin':       usrcfg['isadmin'],
				'edit_self':     usrcfg['edit_self'],
				'server_render': usrcfg['server_render'],
				'torrenting':    usrcfg['torrenting'],
				'edit_thumbs':   usrcfg['edit_thumbs'],
			})
		)

		(details / 'token.lzrd').write_text(
			json.dumps({
				'userid':   usr_id,
				'created':  datetime.datetime.now().isoformat(),
				'crypto':   wfutil.generate_token(),
				'lifetime': 2_000_000,
			})
		)

		(details / 'rules.lzrd').write_text(
			json.dumps({
				'global':             [],
				'shared_rule':        None,
				'apply_shared_after': False,
				'homedir':            '/',
				'target': [
					{
						'rule': '/',
						'prohibit': False,
						'write': True,
						'recursive': False,
						'for_each': {
							'use': False,
							'deep': 2,
							'with_name': '@@',
						}
					}
				],
			})
		)

		(details / 'journal.lzrd').write_text(
			json.dumps({
				'fail':[],
				'ok':[],
			})
		)


		return usr_id


	def init_authdb(self, wipe=False):
		# fuck you
		authdb_root = Path(self.cfg['authdb_path'])
		if not authdb_root.is_dir():
			authdb_root.mkdir(parents=True, exist_ok=True)

		authdb_root = authdb_root / 'authsys'

		if self.dir_condition(authdb_root, wipe):
			return True

		# create all the dirs
		_dirs = (
			'users',
			'details',
			'cfg',
		)
		for d in _dirs:
			(authdb_root / d).mkdir()





		#
		# Create and initialize the user database
		#
		user_db = db_connect(authdb_root / 'users' / 'userdb.db')
		user_db.iexec("""
			CREATE TABLE authdb (
				user_id CHAR(64) NOT NULL UNIQUE,
				login VARCHAR NOT NULL UNIQUE,
				pswd VARCHAR NOT NULL,
				auth_hash CHAR(64) NOT NULL
			);
		""")
		user_db.close()

		#
		# Create admin
		#
		self.create_user({
			'login':         'admin',
			'pswd':          'admin',
			'isadmin':       True,
			'edit_self':     True,
			'server_render': True,
			'torrenting':    True,
			'edit_thumbs':   True,
		})

		#
		# Create default user
		#
		default_user_id = self.create_user({
			'login':         'guest',
			'pswd':          'guest',
			'isadmin':       False,
			'edit_self':     False,
			'server_render': False,
			'torrenting':    False,
			'edit_thumbs':   False,
		})
		(authdb_root / 'cfg' / 'default_user').write_text(default_user_id)


	def init_sysdb(self, wipe=False):
		sysdb_root = Path(self.cfg['sysdb'])
		if self.dir_condition(sysdb_root, wipe):
			return True

		_dirs = (
			'access_tokens',
			'redundancy_list',
			'preview_queue',
			'previews',
			'cgi_err',
			'uploads',
			'temps',
			'uplog',
		)
		for d in _dirs:
			(sysdb_root / d).mkdir()

		#
		# Create and initialize the uploads log
		#
		uplog_db = db_connect(sysdb_root / 'users' / 'uploads.wfb')
		uplog_db.iexec("""
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
		uplog_db.close()







#
# Setup:
#

# Write down config file to the htbin with:
# 	authdb
# 	sysdb
#   xfiles
# 	watchdogs_port
# 	upload_service_port

# create requred db files and folders

# compile htbin_src to htbin with .pyc files inside

# Delete index.html in the web dir
# Move main.html from html_panels to server root with the name index.html

# IF the bins folder is present in the root dir of the system - unpack required files

# Delete the setup dir in the web root


if __name__ == '__main__':
	print('Content-Type: application/octet-stream\r\n\r\n')

	# Get incoming payload with all the params
	incoming_info = json.loads(sys.stdin.buffer.read())

	# Remap some names
	# todo: get rid of this remapping ?
	sv_conf = {
		'ftp_root':            Path( incoming_info.get('ftp_root')            ),
		'ffmpeg':              Path( incoming_info.get('ffmpeg_path')         ),
		'ffprobe':             Path( incoming_info.get('ffprobe_path')        ),
		'magix':               Path( incoming_info.get('magix_path')          ),
		'authdb':              Path( incoming_info.get('authdb_path')         ),
		'sysdb':               Path( incoming_info.get('sysdb_path')          ),
		'xfiles':              Path( incoming_info.get('xfiles')              ),
		# todo: oh cmon, should this shit be strict or not ????
		'watchdogs_port':      int(  incoming_info.get('watchdog_port')       ),
		'upload_service_port': int(  incoming_info.get('upload_service_port') ),
	}

	# Run the setup
	run_s = srv_setup(incoming_info)

	# Delete index.html in the web dir
	# Move main.html from html_panels to server root with the name index.html
	(server / 'index.html').unlink(missing_ok=True)
	shutil.move(server / 'html_panels' / 'main.html', server / 'index.html')

	# Delete the setup dir in the web root
	shutil.rmtree(server / 'setup')



