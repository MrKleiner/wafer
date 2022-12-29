
# Documentation
# 












class fjournal:
	"""a file watcher"""
	# srv = server variable
	def __init__(self, srv):
		self.Path = srv.Path
		self.jdb = srv.sysdb_path / 'journal'
		self.srv = srv
		# ensure that the journal folder exists
		# todo: this is not needed anymore with the new system
		self.jdb.mkdir(exist_ok=True)

	# takes the path to the file and the life length
	# life in hours
	# overwrites previous record, if any
	# important todo: choose whether to overwrite or no
	def reg_file(self, flpath, life=5):
		json = self.srv.json
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

	# manually remove a journal entry
	def unreg_file(self, flpath):
		tgt_unreg = self.Path(flpath)
		unreg_index = self.srv.util.eval_hash(str(flpath), 'sha256')
		(self.jdb / f'{unreg_index}.jr').unlink(missing_ok=True)


	# go through every journal file...
	# todo: create prefixed type which says that every file with this prefix has to be deleted
	def process_jr(self):
		from datetime import datetime
		Path = self.srv.Path

		for jf in self.jdb.glob('*.jr'):
			try:
				# read file contents
				jdata = jf.read_text().split('\n')

				# if the date is older than now - delete the target file
				fl_date = datetime.strptime(jdata[0], '%Y-%m-%d-%H')
				now_date = datetime.now()
				# delete target file
				if fl_date < now_date:
					Path(jdata[1]).unlink(missing_ok=True)
					# delete the task
					jf.unlink(missing_ok=True)
			except Exception as e:
				continue


# server has the following stuff:
# .Path                 = pathlib Path
# .json                 = json module
# .sys                  = sys module
# .output               = sys.stdout.buffer.write = write bytes to the client
# .platform             = which platform this server is running on (windows/linux) (as if there are more than two options)
# .headers              = headers which came with the incoming http request
# .ftp_root             = pathlib Path which points to the FTP root
# .sysdb_path           = util db, like temp files, media previews and media queue
# .authdb_path:         = pathlib Path to the root of the auth db
#     -authsys
#        -users
#            -userdb.db
#        -details
#            ...
#        -cfg
#            -default_user
# .tmp_dir              = temp dir which is allowed to be big
# .server_root          = server root (where index.html is at)
# .util                 = util functions from the util.py file
# .allowed_vid          = recognized video formats
# .allowed_img          = recognized image formats for ffmpeg
# .allowed_img_special  = recognized image formats for imagemagick and not ffmpeg (allows supporting more formats while not loosing too much speed)
# .wfauth               = wafer auth class
# .sv_cfg               = raw server config






class server:
	"""All the stuff passed to the server + server config"""
	# def __init__(self, cgi, sys, cgitb):
	# todo: separate stuff that is not wafer-specific into a function
	def __init__(self):
		# from util import giga_json
		import cgi, sys, cgitb
		from pathlib import Path
		import os
		from server_config import server_config as svconf
		import json, platform
		import wafer_util
		from auth.auth import wfauth

		# traceback messages
		cgitb.enable(format='text')

		self.cgitb = cgitb

		# don't append modules many times...
		self.Path = Path
		self.json = json

		# input sys module
		self.sys = sys

		self.output = sys.stdout.buffer.write

		# buffer to flush
		self.sv_buffer = b''

		# parse url params into a dict, if any
		get_cgi_params = cgi.parse()
		url_params = {}
		for it in get_cgi_params:
			url_params[it] = ''.join(get_cgi_params[it])
		self.prms = url_params

		# parse http headers into a dict, if any
		self.headers = {}
		for hd in os.environ:
			# print(hd, os.environ[hd], '\n')
			if hd.startswith('HTTP_'):
				self.headers[hd.replace('HTTP_', '').lower()] = os.environ[hd]


		# read body content, if any
		self.bin = b''
		# response is the one this script is about to output
		self.response_headers = {}
		try:
			self.bin = sys.stdin.buffer.read()
		except:
			pass

		# server root folder
		for pr in Path(__file__).parents:
			if (pr / 'wafer_root.wfrt').is_file():
				self.server_root = pr
				break

		# todo: just don't bother and distribute two separate versions for linux and for windows ?
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

		# auth db path
		self.authdb_path = Path(self.sv_cfg['authdb'])

		# temp dir for temp files
		self.tmp_dir = self.sysdb_path / 'temps'

		# util functions from the util.py file
		self.util = util

		# also make cgitb write errors to files
		cgitb.enable(format='text', logdir=str(self.sysdb_path / 'cgi_err'))


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
			# IMPORTANT: RECHECK
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
			'hdr',
			'exr'
		]

		# special means ffmpeg cannot deal with it
		self.allowed_img_special = [
			'tga',
			'psd',
			'arw',
			'raw',
			'hdr',
			'exr'
		]


		# self.flush()


		#
		# do auth
		#
		self.wfauth = wfauth(self)



	# journal which keeps track of files to delete
	def journal(self):
		return fjournal(self)



	# @property
	# def tr_type(self):
	# 	return self._tr_type

	# @tr_type.setter
	# def tr_type(self, newname):
		# pass

	# add error header with specified data
	def error(self, err):
		self.set_header('wafer-fatal-error', str(err))

	# spit shit
	# either fill the buffer gradually with .bin_write and then flush
	# or flush bytes immediately by passing bytes to the flush function
	def flush(self, add_b=None):
		if add_b:
			self.bin_write(add_b)
		# add headers
		for h in self.response_headers:
			# try:
			# 	hv = self.response_headers[h].encode()
			# except:
			# 	hv = str(self.response_headers[h]).encode()

			# try:
			# 	h = h.encode()
			# except:
			# 	h = str(h).encode()

			self.output(f'{h}: {self.response_headers[h]}\r\n'.encode())
		# content type
		self.output('Content-Type: application/octet-stream\r\n\r\n'.encode())
		# buffer
		self.output(self.sv_buffer)
		# do flush
		self.sys.stdout.buffer.flush()
		self.sys.stdout.flush()
		self.sys.exit()

	def set_header(self, hkey, hval):
		self.response_headers[hkey] = hval

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

		floc = self.Path(flpath)

		if not floc.is_file():
			raise Exception('x_files transfer: file path does not exist')

		# src from hello.py:
		# sys.stdout.write(b'Content-Type: application/octet-stream\r\n')
		# sys.stdout.write(b'Content-Disposition: attachment; filename="bigfile.mp4"\r\n')
		# sys.stdout.write(b'X-Sendfile: /home/basket/scottish_handshake/db/20181225_182650.ts\r\n\r\n')

		self.output('Content-Type: application/octet-stream\r\n'.encode())
		self.output(f"""Content-Disposition: attachment; filename="{str(flname)}"\r\n""".encode())
		self.output(f"""X-Sendfile: {str(floc)}\r\n\r\n""".encode())

		self.sys.stdout.buffer.flush()
		self.sys.stdout.flush()
		self.sys.exit()


	# it shouldn't be here, but it's here because of performance reasons
	# loads json from a path
	def jload(self, pth):
		return self.json.loads(self.Path(pth).read_bytes())


	# write error traceback to file
	# def filetb(self):
	# 	self.cgitb.


# all requests are evaluated through this file for better error handling
# and action redirection
class md_actions:
	"""Actions"""
	def __init__(self, sv, registry={}):
		self.reg = registry
		self.srv = sv
		self.action = sv.prms.get('action')

	def eval_action(self):
		try:
			# if action from url params is in the registry then execute
			if self.action in self.reg:
				self.reg[self.action]()
			else:
				# todo: is it really a fatal error?
				self.srv.error('invalid_action')
				self.srv.flush(f"""Details: {self.action}, {self.reg}""".encode())
		except Exception as e:
			import sys
			self.srv.output('wafer-fatal-error: raw_exception\r\n'.encode())
			self.srv.output('Content-Type: application/octet-stream\r\n\r\n'.encode())
			# todo: use text/html; charset=UTF-8 instead ?
			# text/html; charset=UTF-8

			# self.srv.set_header('wafer-fatal-error', 'raw_exception')
			# self.srv.flush(str(e).encode())
			raise e




