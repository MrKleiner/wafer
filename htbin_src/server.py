



# server has the following stuff:
# .Path                 = pathlib Path
# .json                 = json module
# .sys                  = sys module
# .os                   = os module
# .output               = sys.stdout.buffer.write = write bytes to the client directly (edge cases)
# .platform             = which platform this server is running on (windows/linux) (as if there could be more than two options)
# .headers              = headers which came with the incoming http request as dict
# .bin_as_json          = evaluate input data to json
# .ftp_root             = pathlib Path which points to the FTP root
# .sysdb_path           = util db, like temp files, media previews and media queue
# .authdb_path:         = pathlib Path to the root of the auth db
# .tmp_dir              = temp dir which is allowed to be big
# .webroot              = server root (where index.html is at)
# .util                 = util functions from the wafer_util.py file
# .allowed_vid          = recognized video formats (ffmpeg)
# .allowed_img          = recognized image formats for ffmpeg
# .allowed_img_special  = recognized image formats for imagemagick and not ffmpeg (allows supporting more formats)
# .wfauth               = wafer auth class
# .sv_cfg               = raw server config


# .rd_journal                  = file journal system
# .bin_as_json                 = tries evaluating input data as json
# .error(error_details)        = spit a fatal error (through header)
# .flush(add_bytes)            = flush existing buffer and exit, optionally adding more bytes
# .flush_json(json)            = flush data as json immediately
# .set_header(hname, hval)     = add header to the response
# .bin_write(bytes)            = append bytes to the response buffer
# .bin_jwrite(json)            = add json to output buffer
# .x_files(filepath)           = transfer file from the specified filepath to the client
# .jload(filepath)             = load json from filepath (pathlib supported)
class server(jag_server):
	"""add wafer-specific stuff to the base server"""
	def __init__(self):
		super().__init__()

		import wafer_util
		from server_config import data as svconf
		from auth.auth import wfauth

		self._xfiles_hname = svconf['xfiles']

		self.wafer_version = '$WAFER_VERSION_NUMBER$'

		# raw server config
		# self.sv_cfg = util.giga_json(self.server_root / 'htbin' / 'server_config.json')
		self.sv_cfg = svconf

		# server root folder
		# todo: can this be faster ?
		# important todo: yes, just grab the second parent
		# for pr in self.Path(__file__).parents:
		# 	if (pr / 'wafer_root.wfrt').is_file():
		# 		self.server_root = pr
		# 		break
		self.webroot = self.Path(__file__).parents[1]


		# system root, aka root of the file pool
		self.ftp_root = self.Path(self.sv_cfg['system_root'])
		
		# util db, like temp files and media previews
		# preview_db
		self.sysdb_path = self.Path(self.sv_cfg['sysdb'])

		# enable cgi traceback asap
		self.cgitb.enable(format='text', logdir=str(self.sysdb_path / 'cgi_err'))

		# auth db path
		self.authdb_path = self.Path(self.sv_cfg['authdb'])

		# temp dir for temp files
		self.tmp_dir = self.sysdb_path / 'temps'

		# util functions from the util.py file
		self.util = wafer_util

		# journal is not always needed
		self._rdjournal = None

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
			# todo: BRO... really ?????
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
	def rd_journal(self):
		if not self._rdjournal:
			self._rdjournal = wafer_redundancy_journal(
				self.sysdb_path / 'redundancy_list',
				self.util,
				self.Path,
				self.json
			)
		return self._rdjournal
















# all requests are evaluated through a jateway for better error handling
# and action redirection

# (it's burned into this file on release compile)