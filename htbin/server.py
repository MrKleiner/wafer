
# Documentation
# 












class fjournal:
	"""a file watcher"""
	# srv = server variable
	def __init__(self, srv):
		from pathlib import Path
		self.Path = Path
		self.jdb = srv.sysdb_path / 'journal'
		self.srv = srv
		# ensure that the journal folder exists
		self.jdb.mkdir(exist_ok=True)

	# takes the path to the file and the life length
	# life in hours
	# overwrites previous record, if any
	# important todo: choose whether to overwrite or no
	def reg_file(self, flpath, life=5):
		import json
		from datetime import datetime, timedelta

		flpath = self.Path(flpath)
		jr_index = self.srv.util.eval_hash(str(flpath), 'sha256')
		jr_tgt = self.jdb / f'{jr_index}.jr'

		jr_tgt.write_bytes(b'')

		tm = (datetime.now() + timedelta(hours=int(life))).timetuple()

		# todo: why bother with this shit when there's json
		# the only advantage of this is that it's PROBABLY a few milliseconds faster...
		with open(str(jr_tgt), 'ab') as j:
			# first line represents timestamp when to delete
			j.write('-'.join([str(tm.tm_year), str(tm.tm_mon), str(tm.tm_mday), str(tm.tm_hour)]).encode())
			j.write('\n'.encode())
			# second line represents file path to delete
			j.write(str(flpath).encode())

	# manually remove journal entry
	def unreg_file(self, flpath):
		tgt_unreg = self.Path(flpath)
		unreg_index = self.srv.util.eval_hash(str(flpath), 'sha256')
		(self.jdb / f'{unreg_index}.jr').unlink(missing_ok=True)


	# go trough every journal file...
	# todo: create prefixed type which says that every file with this prefix has to be deleted
	def process_jr(self):
		from datetime import datetime
		from pathlib import Path
		for jf in self.jdb.glob('*.jr'):
			try:
				# read file contents
				jdata = jf.read_text().split('\n')
				# delete object task immediately
				# todo: does it actually makes sense to delete it immediately ?
				jf.unlink(missing_ok=True)

				# if the date is older than now - delete
				fl_date = datetime.strptime(jdata[0], '%Y-%m-%d-%H')
				now_date = datetime.now()
				# delete target file
				if fl_date < now_date:
					Path(jdata[1]).unlink(missing_ok=True)
			except Exception as e:
				continue


class server:
	"""All the stuff passed to the server + server config"""
	def __init__(self, cgi, sys, cgitb):
		# from util import giga_json
		from pathlib import Path
		from server_config import server_config as svconf
		import json, platform
		import util

		# traceback messages
		cgitb.enable()

		# don't append modules many times...
		self.Pathl = Path
		self.Path = Path
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

		# todo: just don't bother and distribute two separate versions for linux and for windows
		self.platform = platform.system().lower()

		# raw server config
		# self.sv_cfg = util.giga_json(self.server_root / 'htbin' / 'server_config.json')
		self.sv_cfg = svconf

		# system root, aka root of the file pool
		# important todo: better name it ftp_root
		# self.sys_root = Path(self.sv_cfg['system_root'])
		self.ftp_root = Path(self.sv_cfg['system_root'])

		# util db, like temp files and media previews
		# preview_db
		self.sysdb_path = Path(self.sv_cfg['sysdb'])

		# temp dir for temp files
		self.tmp_dir = self.sysdb_path / 'temp_shite'



		# util functions from the util.py file
		self.util = util



		#
		# applicable file formats
		#

		# important todo: this has to be configurable
		# it's not a problem performance wise (declaring 2 vars takes like 0 milliseconds)
		# but it has to be configurable from the control panel

		# one important excuse of this being hardcoded is that some file formats are not supported by ffmpeg
		# but are supported by image magick

		self.allowed_vid = [
			'mp4',
			'mov',
			'webm',
			'ts',
			'mts',
			'mkv',
			'avi',
			'mpeg',
			'ogv',
			'3gp'
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


	# journal which keeps track of files to delete
	def journal(self):
		return fjournal(self)



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

		# src from hello.py:
		# sys.stdout.write(b'Content-Type: application/octet-stream\r\n')
		# sys.stdout.write(b'Content-Disposition: attachment; filename="bigfile.mp4"\r\n')
		# sys.stdout.write(b'X-Sendfile: /home/basket/scottish_handshake/db/20181225_182650.ts\r\n\r\n')

		self.inp_sys.stdout.buffer.write('Content-Type: application/octet-stream\r\n'.encode())
		self.inp_sys.stdout.buffer.write(f"""Content-Disposition: attachment; filename="{str(flname)}"\r\n""".encode())
		self.inp_sys.stdout.buffer.write(f"""X-Sendfile: {str(floc)}\r\n\r\n""".encode())

		self.inp_sys.stdout.buffer.flush()
		self.inp_sys.stdout.flush()
		self.inp_sys.exit()




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




