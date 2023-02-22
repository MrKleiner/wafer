












class wafer_redundancy_journal:

	# srv = reference to the server class
	def __init__(self, srv):
		import datetime
		self.datetime = datetime.datetime
		self.timedelta = datetime.timedelta
		self.Path = srv.Path
		self.jdir = srv.sysdb_path / 'redundancy_list'
		self.srv = srv

	# takes the path to the file and the life length
	# life in hours
	# overwrites previous record, if any
	# important todo: choose whether to overwrite or no
	def reg_file(self, flpath, life=5):
		dtm = self.datetime
		tdelta = self.timedelta

		flpath = str(self.Path(flpath).resolve()).rstrip('/')

		record = {
			'expiration_date': str(dtm.now() + tdelta(hours=int(life))),
			'target': flpath,
		}

		record_id = self.srv.util.eval_hash(flpath, 'sha256')

		(self.jdir / f'{record_id}.jr').write_text(self.srv.json.dumps(record))


	# manually remove a journal entry
	def unreg_file(self, flpath):
		tgt_unreg = str(self.Path(flpath).resolve()).rstrip('/')
		unreg_id = self.srv.util.eval_hash(str(flpath), 'sha256')
		(self.jdir / f'{unreg_index}.jr').unlink(missing_ok=True)




# server has the following stuff:
# .Path                 = pathlib Path
# .json                 = json module
# .sys                  = sys module
# .output               = sys.stdout.buffer.write = write bytes to the client directly (edge cases)
# .platform             = which platform this server is running on (windows/linux) (as if there could be more than two options)
# .headers              = headers which came with the incoming http request as dict
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
# .util                 = util functions from the wafer_util.py file
# .allowed_vid          = recognized video formats (ffmpeg)
# .allowed_img          = recognized image formats for ffmpeg
# .allowed_img_special  = recognized image formats for imagemagick and not ffmpeg (allows supporting more formats)
# .wfauth               = wafer auth class
# .sv_cfg               = raw server config


# .journal                     = file journal system
# .bin_as_json                 = tries evaluating input data as json
# .error(error_details)        = spit a fatal error (through header)
# .flush(add_bytes)            = flush existing buffer and exit, optionally adding more bytes
# .flush_json(json)            = flush data as json immediately
# .set_header(hname, hval)     = add header to the response
# .bin_write(bytes)            = append bytes to the response buffer
# .bin_jwrite(json)            = add json to output buffer
# .x_files(filepath)           = transfer file from the specified filepath to the client
# .jload(filepath)             = load json from filepath (pathlib supported)

class server:
	"""All the stuff passed to the server + server config"""
	# def __init__(self, cgi, sys, cgitb):
	# todo: separate stuff that is not wafer-specific into a function
	def __init__(self):
		# from util import giga_json
		import cgi, sys, cgitb
		import os, json, platform
		import wafer_util
		from pathlib import Path
		from server_config import server_config as svconf
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
		# response headers are the ones this script is about to output to the client
		self.response_headers = {}
		# todo: there are definitely better ways of determining whether the body content could be read or not
		try:
			self.bin = sys.stdin.buffer.read()
		except:
			pass

		# server root folder
		# todo: can this be faster ?
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
		self.util = wafer_util

		# journal is not always needed
		self._journal = None

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

		# video formats supported by ffmpeg
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
			'3gp',
			# todo: but like... really ?????
			'wmv',
			'flv',
		]

		# image formats supported by the combination of ffmpeg and image magick
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
			'exr',
			'dds',
			'ico',
			'pfm',
			'svg',
		]

		# special means ffmpeg cannot deal with it
		# but image magick can
		# the reason ffmpeg is a preferred option is because it works twice as fast compared to imagemagick
		self.allowed_img_special = [
			'tga',
			'psd',
			'arw',
			'raw',
			'hdr',
			# todo: ffmpeg can actually deal with exr files...
			'exr',
			'dds',
			'ico',
			'pfm',
			'svg',
		]


		# self.flush()


		#
		# do auth
		#
		self.wfauth = wfauth(self)



	# journal which keeps track of files to delete
	@property
	def journal(self):
		if not self._journal:
			self._journal = wafer_redundancy_journal(self)
		return 


	def bin_as_json(self):
		return self.json.loads(self.bin)


	# @property
	# def tr_type(self):
	# 	return self._tr_type

	# @tr_type.setter
	# def tr_type(self, newname):
		# pass

	# add error header with specified data
	def fatal_error(self, err):
		self.set_header('wafer-fatal-error', str(err))

	def error(self, err):
		self.set_header('wafer-error', str(err))


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


	def flush_json(self, j):
		self.bin_jwrite(j)
		self.flush()


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



# all requests are evaluated through this gateway for better error handling
# and action redirection
# as of now this is basicaly the gateway and should be called "gateway"
class md_actions:
	"""Actions"""
	def __init__(self, srv, registry={}):
		self.reg = registry
		self.srv = srv
		self.action = self.srv.prms.get('action')

	def eval_action(self):
		try:
			# if action from url params is in the registry then execute
			if self.action in self.reg:
				self.reg[self.action]()
			else:
				# todo: is it really a fatal error?
				self.srv.fatal_error('invalid_action')
				self.srv.flush(f"""Details: Requested: {self.action}, Available: {self.reg}""".encode())
		except Exception as e:
			# The way this works is pretty interesting:

			# When exception occurs upon module action evaluation - 
			# the server outputs a header to the output buffer which indicates that the fatal error occured
			# and then raises the error

			# When an error is raised, the cgitb module adds a PROPERLY FORMATTED error traceback to the output buffer
			# IN ADDITION to the header indicating that a fatal error occured
			# Not only that, but cgitb also dumps the error to the logs folder

			# The most important part is that all of the above happens
			# while keeping the client aware of the said fatal error

			self.srv.output('wafer-fatal-error: raw_exception\r\n'.encode())
			# todo: citb adds appropriate content type automatically
			self.srv.output('Content-Type: application/octet-stream\r\n\r\n'.encode())

			raise e




