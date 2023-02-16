



class media_gen:
	def __init__(self, srv, task):
		# todo: this is literally useless
		# except magix
		# self.ffmpeg = server.Path(server.sv_cfg['ffmpeg'].strip())
		# self.ffprobe = server.Path(server.sv_cfg['ffprobe'].strip())
		self.srv = srv

		self.task = task

		actions = {
			# (DASH)
			'webm':             'self.generate_webm_preview',
			# mouseover preview
			'frame_preview':    'self.generate_vid_preview',
			# image preview
			'img':              self.generate_pic_preview
		}

		actions[task]()

	# get video info with ffprobe
	# takes video path and {stream=}WHATEVER(nb_read_frames,width,height)
	def get_video_stats(self, video_path=None, infos='width,height'):
		import json
		import subprocess as sp

		# ffprobe params
		ffprobe_prms = [
			str(self.ffprobe),
			'-v', 'error',
			'-select_streams', 'v:0',
			'-count_frames',
			'-show_entries',
			# construct query
			f'stream={infos}',
			'-print_format', 'json',
			# target video
			str(video_path)
		]
		video_info = {}
		with sp.Popen(ffprobe_prms, stdout=sp.PIPE, bufsize=10**8) as media_info_pipe:
			# read output of the ffprobe
			video_info = json.loads(media_info_pipe.stdout.read())['streams'][0]

		return video_info

	# this is the only obvious way of doing this
	# aka calling this from js and not waiting for it to return anything
	# todo: store these previews in a shared database where file name is sha256 of a video OR its path
	# to avoid duplicate previews
	# it'd also be important to have controls like re-generating/deleting a preview
	# takes absolute path to the video as an input
	def generate_webm_preview(self, tgt):
		import subprocess as sp
		import os
		from pathlib import Path
		(server.preview_db / 'die.de').write_text('got to generating a webm')

		# just in case - register shit in file journal
		fj = server.journal()

		# get path to the video

		# ORIGINAL
		# vid_path = server.sys_root / server.prms.get('vidpath')
		# NEW
		vid_path = Path(tgt)

		# output dir is the lzpreviews folder
		preview_path = vid_path.parent / 'prdb_lzpreviews' / f'{vid_path.name}.fullvidp.lzpreview.webm'

		# todo: this is where the shit is registered for deletion
		fj.reg_file(f'{preview_path}.fuckoff.webm', 9)
		fj.reg_file(preview_path.with_suffix('.aac'), 4)

		# get video framerate
		# this is needed to drop the video framerate to 25, if needed
		# todo: What's the point of checking this?
		# There are no videos on this planet which have less than 25 fps
		video_info = self.get_video_stats(vid_path, 'r_frame_rate')

		# todo: eval is bad. There are better ways of evaluating maths
		vid_fps = eval(video_info['r_frame_rate'])
		(server.preview_db / 'die.de').write_text('webm setups done')
		

		# create ffmpeg params
		ffmpeg_prms = [
			# ffmpeg executable
			str(self.ffmpeg),

			# automatically discard if file exists
			'-n',

			# limit CPU thread usage
			'-threads', '2',

			# input file
			'-i', str(vid_path),

			# filters: clamp to width
			'-vf', 'scale=w=min(iw\\,420):h=-2' if vid_fps <= 25 else """scale='w=min(iw\\,420):h=-2', fps='fps=25'""",

			# audio
			'-acodec', 'libopus',
			'-b:a', '86k',

			# video encoding shit
			'-c:v', 'libvpx-vp9',

			# OLD
			# '-minrate', '50k',
			# '-b:v', '120k',
			# '-maxrate', '700k',

			# NEW
			'-crf', '51',

			# save extra space
			'-deadline', 'best',

			# output file location
			str(f'{preview_path}.fuckoff.webm')
		]


		# ffmpeg -i video.mp4 -f mp3 -ab 192000 -vn music.mp3
		audio_prms = [
			# ffmpeg executable
			str(self.ffmpeg),

			# automatically discard if file exists
			'-n',

			# input file
			'-i', str(vid_path),

			# audio

			# OLD
			# '-acodec', 'aac',
			# '-b:a', '96k',

			# NEW
			'-c:a', 'libvorbis',
			'-b:a', '50k',
			'-minrate', '10k',
			'-maxrate', '50k',

			# vn = no video
			'-vn',

			# output file location
			str(preview_path.with_suffix('.ogg'))
		]
		wat = None
		with sp.Popen(ffmpeg_prms, stdout=sp.PIPE, bufsize=10**8) as img_pipe:
			wat = img_pipe.stdout.read()

		# захуярь раммштайн
		webp = None
		with sp.Popen(audio_prms, stdout=sp.PIPE, bufsize=10**8) as img_pipe:
			webp = img_pipe.stdout.read()

		(server.preview_db / 'die.de').write_text('ffmepeg was executed ok')
		
		# sp.Popen(audio_prms)
		# sp.Popen(ffmpeg_prms)

		# rename stuff once done encoding
		os.rename(str(f'{preview_path}.fuckoff.webm'), str(preview_path))
		
		# todo: this is where shit is unregistered
		fj.unreg_file(f'{preview_path}.fuckoff.webm')
		fj.unreg_file(preview_path.with_suffix('.aac'))

		(server.preview_db / 'die.de').write_text('done generating webm')

		# flush the shit ?
		# lmao no. this will kill he python process...
		# server.flush('ok'.encode())


	# obvious todo: hardcoded 100 frames = bad
	# takes video path as an input
	# and returns a location of the .chad file
	def generate_vid_preview(self, vidpath):
		import sys, json, shutil
		import subprocess as sp
		from pathlib import Path
		sys.path.append('.')
		from gigabin_py import gigabin
		#
		# ffmpeg.exe -i "C:\Users\baton\Downloads\hacker-1-5.mp4" -vf select="eq(n\,10)+eq(n\,27)+eq(n\,31)" -vsync 0 -c:v libwebp -f image2 -lossless 0 -compression_level 6 -qscale 50 "C:\custom\other\ffmpeg_test\hax%d.webp"
		#

		# old ver
		# ffmpeg -i in.mp4 -vf select='eq(n\,100)+eq(n\,184)+eq(n\,213)' -vsync 0 frames%d.jpg

		# file journal
		# keep track of frames n shit
		# the less rubbish there is the better
		fj = server.journal()

		# important todo: is it really a good place to evaluate the entire journal ?
		# update: this is now done in the queue process
		# fj.process_jr()

		# preview db location
		prdb = server.preview_db
		# target video location
		# tgt_vid = Path(server.prms['media_path'])
		tgt_vid = Path(vidpath)
		if not tgt_vid.is_file():
			raise Exception('generate_vid_preview: video does not exist under the specified file path')

		# todo: also evaluate file checksum ?
		# preview_name = server.util.eval_hash(str(tgt_vid), 'sha256')
		# the hash of the video is also its preview name, for now
		# inp_video_hash = server.util.hash_file(str(tgt_vid), 'sha256')
		preview_file_name = server.util.hash_file(str(tgt_vid), 'sha256')

		# todo: create a quick table of frame extraction amount
		# aka 1hr video = 200 frames, 10 minute video = 50 frames ...







		# ==========================================================
		# Queue mechanism
		# ==========================================================

		# todo: so what about locking the preview generation ?
		# for now generate a lock file and don't generate shit if it exists
		# obviously, add it to journal so that it cannot be fucked forever
		# right now the problem is that a new gigabin is generated each time
		# this is quite expensive
		# the gigabin lib should either support generating virtual files
		# or just some other solution...
		# update: even with the queue system - it's better to be giga safe
		# and have like a secondary lock
		lockpath = (server.tmp_dir / f'{preview_file_name}.goaway')
		if lockpath.is_file():
			return

		lockpath.write_bytes('no really, fuckoff'.encode())
		fj.reg_file(lockpath)







		# ==========================================================
		# first, get resolution and frame count of the video
		# ==========================================================

		# ffprobe.exe -v error -select_streams 0 -count_frames -show_entries stream=nb_read_frames,width,height -print_format json "C:\Users\baton\Downloads\hacker-1-5.mp4"
		# OLD LOCAL APPROACH
		"""
		ffprobe_prms = [
			'/usr/bin/ffprobe',
			'-v', 'error',
			'-select_streams', 'v:0',
			'-count_frames',
			'-show_entries',
			'stream=nb_read_frames,width,height',
			'-print_format', 'json',
			str(tgt_vid)
		]
		vid_res = None
		vid_fr_count = None
		with sp.Popen(ffprobe_prms, stdout=sp.PIPE, bufsize=10**8) as img_info_pipe:
			# read output of the ffprobe
			vid_info = json.loads(img_info_pipe.stdout.read())['streams'][0]
			# save resolution XY
			vid_res = (int(vid_info['width']), int(vid_info['height']))
			vid_fr_count = int(vid_info['nb_read_frames'])
		"""
		vid_info = self.get_video_stats(tgt_vid, 'nb_read_frames,width,height')
		vid_res = (int(vid_info['width']), int(vid_info['height']))
		vid_fr_count = int(vid_info['nb_read_frames'])






		# ==========================================================
		# Now, construct ffmpeg params for frames extraction and execute frame extraction
		# ==========================================================

		# important todo: finally create a frame table
		frc = 100 if vid_fr_count > 100 else vid_fr_count - 1

		# frame selection filter
		frame_nums = '+'.join([f'eq(n\\,{int(frnum)})' for frnum in server.util.even_points(1,vid_fr_count,frc)])
		# ffmpeg execution params
		# it's very important to note that ffmpeg frame extraction count starts at 1 and NOT 0
		ffmpeg_prms = [
			# ffmpeg executable
			str(self.ffmpeg),

			# automatically overwrite if file exists already
			'-y',

			# limit CPU thread usage
			'-threads', '2',
			
			# input file
			'-i', str(tgt_vid),

			# filters: frame selection and width clamping
			'-vf', f"""select='{frame_nums}', scale='w=min(iw\\,400):h=-2'""",
			# this is a VERY important option, without this all frames of the videos are extracted
			'-vsync', '0',

			# compression
			'-c:v', 'libwebp',

			'-lossless', '0',
			'-compression_level', '6',
			'-qscale', '20',

			# output file location
			str(prdb / 'temp_shite' / f'{preview_file_name}%d.btgsystmp.webp')
		]

		# extract frames to a temp location
		# todo: the output of this command doesn't really has to be captured
		# because ffmpeg puts frames into corresponding location by itself
		echo_sh = None
		with sp.Popen(ffmpeg_prms, stdout=sp.PIPE, bufsize=10**8) as frame_ext_echo:
			echo_sh = frame_ext_echo.stdout.read()

		# todo: there's a million fucking ways to run shit...
		# sp.run(ffmpeg_prms)
		# server.flush(' '.join(ffmpeg_prms).encode())





		# ===============================================
		# collapse frames and info into a gigabin
		# ===============================================

		# init new gigabin
		chad_location = prdb / 'temp_shite' / f'{preview_file_name}.chad'
		chad = gigabin(chad_location, True)

		# register gigabin for deletion
		fj.reg_file(chad_location, 1)

		# add frames to gigabin one by one
		for vframe in range(frc):
			# it's very important to note that ffmpeg frame extraction count starts at 1 and NOT 0
			giga_name = (prdb / 'temp_shite' / f'{preview_file_name}{vframe+1}.btgsystmp.webp')
			chad.add_solid(
				fname 		= f'frn{vframe+1}',
				data 		= giga_name.read_bytes(),
				overwrite 	= False,
				dohash 		= False
			)
			# delete file afterwards
			giga_name.unlink(missing_ok=True)

		# write down info about this preview bin
		index_json = {
			# video dimensions
			'dimensions': vid_res,
			# frame count
			'frame_count_total': vid_fr_count,
			#
			'preview_frame_count': frc,
			# tell client that it exists
			'exists': True,
			# test
			'lizards': 'sexy'
			# 'debug': str(prdb / 'temp_shite' / f'{preview_file_name}{1}.webp')
		}
		# add this json to gigabin
		chad.add_solid(
			fname 		= 'index',
			data 		= json.dumps(index_json).encode(),
			overwrite 	= True,
			dohash 		= False
		)


		# finally, return gigabin with all the previews
		# return (prdb / 'temp_shite' / f'{preview_name}.chad').read_bytes()
		# server.x_files((prdb / 'temp_shite' / f'{preview_file_name}.chad'), 'video_preview')

		# important todo: this is where the shit is unlocked
		lockpath.unlink()
		# lock file unreg
		fj.unreg_file(lockpath)
		# giga bin unreg
		fj.unreg_file(chad_location)

		# return path to the .chad file
		# return chad_location

		# update: there's no return anymore, this function has to move the file by itself
		newloc = tgt_vid.parent / 'prdb_lzpreviews' / f'{tgt_vid.name}.lzpreview.chad'
		shutil.move(str(chad_location), str(newloc))


	# important todo: https://trac.ffmpeg.org/wiki/Encode/VP9
	# generate a lowres preview of a static image
	def generate_pic_preview(self):
		import subprocess as sp
		from pathlib import Path

		rel_path = self.task['input'].strip('/')

		img_path = self.srv.ftp_root / rel_path

		if not img_path.is_file():
			raise Exception('generate_pic_preview: image does not exist under the specified file path')

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

