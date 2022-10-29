
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
		import json
		import util

		# traceback messages
		cgitb.enable()

		# don't append modules many times...
		self.Pathl = Path
		self.json = json

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
		for pr in Path(__file__).parents:
			if (pr / 'htbin').is_dir():
				self.server_root = pr
				break

		# raw server config
		self.sv_cfg = util.giga_json(self.server_root / 'htbin' / 'server_config.json')

		# system db with other folders, like previews and temp shit
		self.preview_db = Path(self.sv_cfg['preview_db'])

		# system root, aka root of the file pool
		self.sys_root = Path(self.sv_cfg['system_root'])

		# temp dir for temp files
		self.tmp_dir = self.preview_db / 'temp_shite'

		# self.user_token = self.auth_db.get(url_params.get('auth'))
		self.util = util


		#
		# applicable formats
		#

		self.allowed_vid = [
			'mp4',
			'mov',
			'webm',
			'ts',
			'mts',
			'mkv',
			'avi'
		]

		self.allowed_img = [
			'jpg',
			'jpeg',
			'jp2',
			'j2k',
			'png',
			'tif',
			'tiff',
			'tga',
			'webp',
			'psd',
			'apng',
			'gif',
			'avif',
			'bmp',
			'dib',
			'raw',
			'arw',
			'jfif',
			'jif',
			'hdr'
		]

		self.allowed_img_special = [
			'tga',
			'psd',
			'arw',
			'raw',
			'hdr'
		]


	# @property
	# def tr_type(self):
	# 	return self._tr_type

	# @tr_type.setter
	# def tr_type(self, newname):
		# pass


	# spit shit
	# pass bytes to first add these bytes to the buffer and THEN flush
	def flush(self, add_b=None):
		if add_b:
			self.bin_write(add_b)
		# general info
		self.inp_sys.stdout.buffer.write('Content-Type: application/octet-stream\r\n\r\n'.encode())
		# buffer
		self.inp_sys.stdout.buffer.write(self.sv_buffer)
		# do flush
		self.inp_sys.stdout.buffer.flush()
		self.inp_sys.stdout.flush()
		self.inp_sys.exit()


	# add to bin
	# expects bytes
	def bin_write(self, dat):
		if not isinstance(dat, bytes):
			raise Exception('Cant add anything besides bytes to output buffer')

		self.sv_buffer += dat

	# add json to bin
	def bin_jwrite(self, jsn):
		self.sv_buffer += self.json.dumps(jsn).encode()


	# spit file
	def x_files(self, flpath, flname):

		if not flpath or not flname:
			raise Exception('x_files transfer: one of the arguments is completely invalid')

		floc = self.Pathl(flpath)

		if not floc.is_file():
			raise Exception('x_files transfer: file path does not exist')

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
		db_obj = self.json.loads(db_pt.read_bytes())
		return server_logpswd_db(db_obj, db_pt)

	# allowance, like admin and modules
	@property
	def alw_db(self):
		db_pt = self.Pathl(self.sv_cfg['clearance_db'])
		db_obj = self.json.loads(db_pt.read_bytes())
		return server_allowance_db(db_obj, db_pt)





class md_actions:
	"""Actions"""
	def __init__(self, sv, registry={}):
		self.reg = registry
		self.srv = sv
		self.action = sv.prms.get('action')

	def eval_action(self):
		# if action from url params is in the registry then execute
		if self.action in self.reg:
			self.reg[self.action]()
		else:
			self.srv.bin_write('invalid action'.encode())
			self.srv.flush()