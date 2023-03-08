


# cfg is a dict where:
# {
# 	'loc':{
# 		'ftproot': path to the root of the FTP,
# 		''
# 	},
# 	'specs': {
# 		media gen specs from mediagen.lzrd
# 	},
# 	'software': {
# 		'ffmpeg': absolute path to ffmpeg,
# 		'ffprobe': absolute path to ffprobe,
# 		'magix': absolute path to magix,
# 	},
# }

# task is a dict describing the task
class media_gen:
	def __init__(self, cfg, task):
		from pathlib import Path
		import wafer_util
		self.wutil = wafer_util
		self.Path = Path

		# important todo: reading config on each media gen instance is certainly not performance-friendly
		self.cfg = cfg

		self.task = task

		# input file location
		self.finput = Path(task['input'])

		self.ext_dict = {
			'img': '.wfpic',
			'scroll': '.wfscroll',
			'dash': '.wfdash',
		}

		# path to the source file hashed with sha256
		self.nameid = self.wutil.eval_hash(str(self.finput).strip('/'), 'sha256')

		# output file location
		if task['output'] != None:
			self.output = Path(task['output'])
			if self.output.is_dir():
				self.output = self.output / f'{self.nameid}.{self.ext_dict[task]}'
		else:
			# otherwise - use default location
			self.output = Path(self.cfgctrl.sysc_cache['sysdb']) / 'previews' / f'{self.nameid}.{self.ext_dict[task]}'

		actions = {
			'img': self.gen_pic_preview,
		}

		# Execute corresponding action
		actions[task]()





	# important todo: https://trac.ffmpeg.org/wiki/Encode/VP9
	# generate a lowres preview of a static image
	def gen_pic_preview(self):
		import subprocess as sp
		Path = self.Path

		if not self.finput.is_file():
			raise Exception(f'generate_pic_preview: image does not exist under the specified file path {str(self.finput)}')






		# important todo: https://trac.ffmpeg.org/wiki/Encode/VP9
		ffmpeg_prms = [
			# mpeg
			# todo: use path from server config
			'/usr/bin/ffmpeg',
			# input
			# '-i', str(engines / pl['img']),
			'-i', str(img_path),
			# resize
			# '-hwaccel', 'cuda',
			# '-hwaccel_output_format', 'cuda',
			# '--enable-nvenc',
			# '--enable-ffnvcodec',
			# '-h', 'encoder=h264_nvenc',
			# does nothing
			# (it works, but it's only for videos)
			# '-vcodec', 'h264_nvenc',
			# change size
			# this will upscale sometimes
			# '-vf', 'scale=500:-1',
			# while this is smart
			# this is quite a hires preview
			# '-vf', 'scale=w=min(iw\\,500):h=-2',
			# this one is smaller
			'-vf', 'scale=w=min(iw\\,300):h=-2',
			# format
			'-c:v', 'webp',
			# ffmpeg encoding type
			'-f', 'image2pipe',
			# lossless
			# quite a heavy load
			# '-lossless', '1',
			# make it take even less space
			'-lossless', '0',
			# lossless compression
			# (now is lossy)
			'-compression_level', '6',
			'-qscale', '40',
			# output to stdout
			'pipe:'
			# 'fuckoff.webp'
			# str(tgt_path.parent / 'prdb_lzpreviews' / f'{tgt_path.name}.lzpreview.webp')
		]

		# webp = subprocess.run(ffmpeg_prms, capture_output=True)
		webp = None
		with sp.Popen(ffmpeg_prms, stdout=sp.PIPE, bufsize=10**8) as img_pipe:
			# myFile.write(img_pipe.stdout.read())
			webp = img_pipe.stdout.read()

		if self.task['output'] == ':pipe':
			return webp

		(self.srv.sysdb_path / 'previews' / f"""{self.srv.util.eval_hash(str(rel_path).strip('/').encode(), 'sha256')}.webp""").write_bytes(webp)

		if self.task['output'] == ':both':
			return webp

