
class server_logpswd_db:
	def __init__(self, obj, db_path):
		self.db = obj
		self.path = db_path

class server_allowance_db:
	def __init__(self, obj, db_path):
		self.db = obj
		self.path = db_path





class server:
	"""All the stuff passed to server + server config"""
	def __init__(self, cgi, sys, cgitb):
		# from util import giga_json
		from pathlib import Path
		import util

		# traceback messages
		cgitb.enable()

		self.Pathl = Path

		# input sys module
		self.inp_sys = sys

		# buffer to flush
		self.sv_buffer = b''

		# parse url params into a dict, if any
		get_cgi_params = cgi.parse()
		url_params = {}
		for it in get_cgi_params:
			url_params[it] = ''.join(get_cgi_params[it])
		self.prms = url_params

		# read body content, if any
		self.bin = b''
		try:
			self.bin = sys.stdin.buffer.read()
		except:
			pass

		# server root folder
		self.server_root = Path(__file__).parent.parent

		# raw server config
		self.sv_cfg = util.giga_json(server_root / 'htbin' / 'server_config.json')

		# system db with other folders, like previews and temp shit
		self.preview_db = Path(self.sv_cfg['preview_db'])

		# system root, aka root of the file pool
		self.sys_root = Path(self.sv_cfg['system_root'])

		# self.user_token = self.auth_db.get(url_params.get('auth'))
		self.util = util


	# @property
	# def tr_type(self):
	# 	return self._tr_type

	# @tr_type.setter
	# def tr_type(self, newname):
		# pass


	# spit shit
	def flush(self):
		# general info
		self.inp_sys.stdout.buffer.write('Content-Type: application/octet-stream\r\n'.encode())
		# buffer
		self.inp_sys.stdout.buffer.write(self.sv_buffer)
		# do flush
		self.inp_sys.stdout.buffer.flush()
		self.inp_sys.stdout.flush()
		sys.exit()


	# add to bin
	# expects bytes
	def bin_write(self, dat):
		if not isinstance(dat, bytes):
			raise Exception('Cant add anything besides bytes to output buffer')

		self.bin += dat

	# spit file
	def x_files(self, flpath, flname):
		from pathlib import Path

		if not flpath or not flname:
			raise Exception('x_files transfer one of the arguments is completely invalid')

		floc = Path(flpath)

		if not floc.is_file():
			raise Exception('x_files transfer file path does not exist')

		self.inp_sys.stdout.buffer.write('Content-Type: application/octet-stream\r\n'.encode())
		self.inp_sys.stdout.buffer.write(f"""Content-Disposition: attachment; filename="{str(flname)}"\r\n""".encode())
		self.inp_sys.stdout.buffer.write(f"""X-Sendfile: {str(floc)}\r\n\r\n""".encode())

		self.inp_sys.stdout.buffer.flush()
		self.inp_sys.stdout.flush()
		self.inp_sys.exit()


	# login,password,token database
	@property
	def auth_db(self):
		db_pt = self.Pathl(self.sv_cfg['auth_db_loc'])
		db_obj = json.loads(db_pt.read_bytes())
		return server_logpswd_db(db_obj, db_pt)

	# allowance, like admin and modules
	@property
	def alw_db(self):
		db_pt = self.Pathl(self.sv_cfg['clearance_db'])
		db_obj = json.loads(db_pt.read_bytes())
		return server_allowance_db(db_obj, db_pt)




