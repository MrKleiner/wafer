import cgi, sys, cgitb
sys.path.append('..')
from server import server, md_actions
server = server(cgi, sys, cgitb)


# File imports
import asyncio



# media generator
# only has a few functions, but still it's better to have it as a separate class
class media_gen:
	def __init__(self):
		self.dd = 'dd'


	# get video info with ffprobe
	# takes  video path and {stream=}WHATEVER(nb_read_frames,width,height)
	def get_video_stats(self, video_path=None, infos='width,height'):
		import json
		import subprocess as sp

		# ffprobe params
		ffprobe_prms = [
			'/usr/bin/ffprobe',
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
	# important todo: store these previews in a shared database where file name is sha256 of a video OR its path
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
			'/usr/bin/ffmpeg',

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
			'/usr/bin/ffmpeg',

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
			'/usr/bin/ffmpeg',

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






# This is responsible for precessing the media preview generation queue
class mqueue:
	def __init__(self):

		# init the mediagen class
		self.mgen = media_gen()

		# store possible actions
		self.actions = {
			'webm':				self.mgen.generate_webm_preview,
			'frame_preview':	self.mgen.generate_vid_preview
		}

		# shortcut to the queue folder
		self.qdb = server.preview_db / 'preview_queue'

	# this writes an error log to a file
	def errlog_exc(self, err):
		# import traceback
		# append the error
		with open(str(server.preview_db / 'preview_queue' / 'errlog.err'), 'ab') as erl:
			# exc_str = traceback.format_exception(err)
			erl.write('\n\n'.encode())
			erl.write(str(err).encode())
			erl.write('\n'.encode())
			# erl.write(str(''.join(exc_str)).encode())

	# and this writes a custom error log to the same file
	def errlog_manual(self, err):
		# append the error
		with open(str(server.preview_db / 'preview_queue' / 'errlog.err'), 'ab') as erl:
			erl.write('\n\n\n--------------- Manual Error ---------------'.encode())
			erl.write(str(err).encode())

	# resume the queue
	# basically, this ensures that the queue is running
	# (it's also the queue process itself)
	def resume(self):
		import json, os
		from pathlib import Path

		(server.preview_db / 'die.de').write_text('called resume shit')

		# first of all - check whether the queue is running already or not
		qdb = self.qdb

		# if it's working - don't do anything
		q_lock_file = (qdb / 'q_is_working.sandwich')
		if q_lock_file.is_file():
			server.flush('queue is working aready'.encode())

		# else - create the file and obviously, add it to journal
		# and start working on the queue
		fj = server.journal()
		# create the lock file
		q_lock_file.write_bytes('sandwich'.encode())
		# add this file to the journal
		# todo: there has to be an option to prolongue the item life time
		fj.reg_file(q_lock_file, 12)

		# keep going trough the items in the queue
		# every item is a json dict where:
		# input: absolute file path of target item
		# output: absolute destination filepath
		# task: what to do with the given file
		# 	valid entries are: webm/frame_preview
		while True:
			# get a queue entry
			# try to get all the items from the folder
			all_items = [itp for itp in qdb.glob('*.qi')]
			# if the list is empty - it means that there's nothing to do
			if len(all_items) <= 0:
				break

			# if there's at least one entry - get it
			# actually, get the last one
			# because getting the first one may result in the older entries never being reached
			# todo: wait, does this logic make any sense?
			current_item = all_items[-1]

			# evaluate the task
			task_d = json.loads(current_item.read_bytes())
			inp_loc = Path(str(task_d['input']))
			# outp_loc = Path(str(task_d['output']))

			# don't do shit if input or output is invalid
			# todo: for now there's only input
			# if not inp_loc.is_file() or not inp_loc.parent.is_file():
			if not inp_loc.is_file():
				self.errlog_manual(f'file: {str(current_item)}, error: input or output does not exist')
				# indicate that this file is broken
				os.rename(str(current_item), str(current_item.with_suffix('.broken')))
				continue

			# actually, run the file journal process
			# because there's a plenty of time available
			# which means that a few seconds for the journal task is not a problem
			# but first of all - extend the lock lifetime

			# todo: the lock file is literally the thing which keeps 70% of the system together
			# if something goes wrong with the lock file mechanism - everything is fucked
			fj.reg_file(q_lock_file, 12)
			fj.process_jr()

			# do what was asked
			# important todo: there's an assumption that all functions take exactly one parameter
			# and that this parameter is an input file path
			self.actions[task_d['task']](inp_loc)

			# once done with the action - delete the task file
			current_item.unlink(missing_ok=True)




		# once done with the queue - remove the lock file
		q_lock_file.unlink(missing_ok=True)
		# and uregister it from the journal
		fj.unreg_file(q_lock_file)

	# add an item to the registry
	# takes the path of the target video
	# and the task type
	# important todo: for now the target path is also an id of the task
	def reg_item(self, tgt_path, tsk):
		import json
		rg_info = json.dumps({
			'input': str(tgt_path),
			'output': None,
			'task': str(tsk)
		})

		# task id is an asbolute filepath + --task_type--
		task_id = server.util.eval_hash(f'{str(tgt_path)}--{str(tsk)}--', 'sha256')
		# if this task exists already - don't do shit
		if (self.qdb / f'{task_id}.qi').is_file():
			return 'task exists'

		# else - add it to the registry
		(self.qdb / f'{task_id}.qi').write_bytes(rg_info.encode())
		return 'registered a new task'





# important todo: https://trac.ffmpeg.org/wiki/Encode/VP9
class poolsys:

	def __init__(self):
		# import json
		# from pathlib import Path
		self.mediaq = mqueue()



	def list_leagues(self):
		import json

		server.bin_jwrite([fld.name for fld in server.sys_root.glob('*') if fld.is_dir()])
		# server.bin_write(str(server.sys_root).encode())
		server.flush()


	def list_matches_w_subroot(self):
		import json

		mws = {}
		for cmd in server.sys_root.glob('*'):
			if not cmd.is_dir():
				continue
			mws[cmd.name] = [match.name for match in cmd.glob('*') if match.is_dir()]

		server.bin_jwrite(mws)
		server.flush()



	def list_league_matches(self):
		import json
		from pathlib import Path

		if not server.prms['league_name']:
			return []

		server.bin_jwrite([fld.name for fld in (server.sys_root / Path(server.prms['league_name'])).glob('*') if fld.is_dir()])
		server.flush()



	def list_match_struct(self):
		import json
		from pathlib import Path

		server.bin_jwrite([fld.name for fld in (server.sys_root / Path(server.prms['match_name'])).glob('*') if fld.is_dir()])
		server.flush()


	def list_media(self):
		import json, os
		from pathlib import Path

		matches = []
		# todo: continue statements were cool
		for match in (server.sys_root / Path(server.prms['target'])).glob('*'):
			if match.is_dir():
				continue

			fl_info = {
				'lfs': (True if os.stat(str(match)).st_size >= ((1024**2)*3) else False),
				'stats': f"""{((1024**2)*3)}/{os.stat(str(match)).st_size}""",
				'etype': 'file',
				'path': str(match.relative_to(server.sys_root)),
				'flname': match.name
			}

			if match.suffix.strip('.').lower() in server.allowed_vid:
				fl_info['etype'] = 'vid'
			if match.suffix.strip('.').lower() in server.allowed_img:
				fl_info['etype'] = 'img'

			matches.append(fl_info)


		server.bin_jwrite(matches)
		server.flush()



	# important todo: https://trac.ffmpeg.org/wiki/Encode/VP9
	# generate a lowres preview of a static image
	def generate_pic_preview(self, img_path=None):
		import subprocess as sp
		from pathlib import Path

		img_path = Path(img_path)
		if not img_path.is_file():
			raise Exception('generate_pic_preview: image does not exist under the specified file path')

		# important todo: https://trac.ffmpeg.org/wiki/Encode/VP9
		ffmpeg_prms = [
			# mpeg
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
			'-vf', 'scale=w=min(iw\\,400):h=-2',
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
			'-qscale', '50',
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

		return webp

	# basically an image preview gateway
	def load_image_preview(self):
		import json
		from pathlib import Path

		# target image filepath
		tgt_path = server.sys_root / Path(server.prms['image_path'])

		# if requested file is not of supported format - return error
		if not tgt_path.suffix.strip('.').lower() in server.allowed_img:
			server.flush('Requested files does not match any supported image formats'.encode())

		# if this file exists in the previews pool - get it and return immediately
		preview_path = (tgt_path.parent / 'prdb_lzpreviews' / f'{tgt_path.name}.lzpreview.webp')
		if preview_path.is_file():
			server.x_files(preview_path, preview_path.name)

		# create the folder with previews if it doesn't exist
		(tgt_path.parent / 'prdb_lzpreviews').mkdir(exist_ok=True)

		# generate the preview
		webp = self.generate_pic_preview(tgt_path)

		# Save preview to the preview folder
		preview_path.write_bytes(webp)

		# return webp bytes to the client
		server.flush(webp)


	# just like with videos - a gateway...
	# todo: separate this stuff into a special class ?
	def load_video_preview(self):
		from pathlib import Path
		import shutil, json
		sys.path.append('.')
		from gigabin_py import gigabin

		# target video filepath (absolute)
		tgt_path = server.sys_root / Path(server.prms['video_path'])

		# if requested file is not of supported format - return error
		if not tgt_path.suffix.strip('.').lower() in server.allowed_vid:
			server.flush('Requested file does not match any supported video formats'.encode())
		
		# if this file exists in the previews pool - get it and return immediately
		preview_path = (tgt_path.parent / 'prdb_lzpreviews' / f'{tgt_path.name}.lzpreview.chad')
		if preview_path.is_file():
			server.x_files(preview_path, preview_path.name)

		# else - queue the preview generation
		# create the folder with previews if it doesn't exist
		(tgt_path.parent / 'prdb_lzpreviews').mkdir(exist_ok=True)

		# register a preview generation task
		# rum = self.generate_vid_preview(tgt_path)
		# important todo: does it make sense to generate the webm preview here as well ?
		# or rather, even though this is the only place where it's being registered
		# and it's impossible to overwrite previous records - should there be a better
		# mechanism of preventing the same file from being generated 2+ times ?
		self.mediaq.reg_item(tgt_path, 'frame_preview')
		self.mediaq.reg_item(tgt_path, 'webm')
		# ensure that the queue is running
		# self.mediaq.resume()

		# lie to the client that the preview is still generating
		giga_temp = server.tmp_dir / f'{server.util.generate_token()}.systmp'
		# create an empty gigabin
		stilgen = gigabin(giga_temp, True)
		# fj.reg_file(lockpath.with_suffix('systmp'), 1)
		fake_json = {
			'exists': False
		}
		# add this json to gigabin
		stilgen.add_solid(
			fname 		= 'index',
			data 		= json.dumps(fake_json).encode(),
			overwrite 	= True,
			dohash 		= False
		)
		tmpbuf = giga_temp.read_bytes()
		giga_temp.unlink(missing_ok=True)
		server.flush(tmpbuf)




		#
		# OLD
		#

		# unregister chad location
		# todo: not needed ?
		# fj = server.journal()

		# move the preview to the previews folder
		# newloc = tgt_path.parent / 'prdb_lzpreviews' / f'{tgt_path.name}.lzpreview.chad'
		# shutil.move(str(rum), str(newloc))

		# unreg
		# fj.unreg_file(rum)

		# send generated file to client
		# server.x_files(newloc, newloc.name)



	# load a fullres image
	def load_fullres_pic(self):
		# from pathlib import Path
		import os
		if os.stat(server.sys_root / server.prms['target']).st_size > ((1024**2)*50):
			return 'file is too big'.encode()

		server.x_files((server.sys_root / server.prms['target']), 'preview')


	def temp_resume_shit(self):
		import traceback
		try:
			self.mediaq.resume()
		except Exception as e:
			# exc_str = traceback.format_exception(e)
			(server.preview_db / 'dieSHIT.fuck').write_text(str(e))


	# important todo: check whether the file exists before loading
	# load lowres webm preview
	def get_webm(self):
		tgt_path = server.sys_root / server.prms.get('vidpath')
		server.x_files((tgt_path.parent / 'prdb_lzpreviews' / f'{tgt_path.name}.fullvidp.lzpreview.webm'), 'webmvideo.webm')

	# load audio of the file
	def get_webm_audio(self):
		tgt_path = server.sys_root / server.prms.get('vidpath')
		server.x_files((tgt_path.parent / 'prdb_lzpreviews' / f'{tgt_path.name}.fullvidp.lzpreview.ogg'), 'audio.ogg')

	# check whether the webm preview is still generating, fully generated alr or missing completely
	def check_webm_status(self):
		tgt_path = server.sys_root / server.prms.get('vidpath')
		full_vid = (tgt_path.parent / 'prdb_lzpreviews' / f'{tgt_path.name}.fullvidp.lzpreview.webm').is_file()
		still_gen = (tgt_path.parent / 'prdb_lzpreviews' / f'{tgt_path.name}.fullvidp.lzpreview.webm.fuckoff.webm').is_file()
		
		server.bin_jwrite({
			'full': full_vid,
			'generating': still_gen,
			'missing': not full_vid and not still_gen
		})
		server.flush()

	# it's called lik that, because this is literally what it does:
	# it ensures that the webm generation is queued
	def ensure_webm_generation(self):
		# even though the path validity would be checked later by the queue mechanism
		# ensure that the path is valid now too
		vid_path = server.sys_root / server.prms.get('vidpath')
		if not vid_path.is_file():
			server.bin_jwrite({
				'status': 'fail',
				'reason': 'target file does not exist'
			})
			server.flush()

		# else - add it to the queue
		rg_reply = self.mediaq.reg_item(vid_path, 'webm')

		# be polite: notify the client
		server.bin_jwrite({
			'status': 'ok',
			'details': str(rg_reply)
		})
		server.flush()



	# todo: temp. donwload a video
	def dl_vid(self):
		tgt_p = server.sys_root / server.prms['dl_tgt']
		server.x_files(tgt_p, tgt_p.name)

	# todo: temp. donwload a video
	# get the actual fucking command you genius
	def get_dl_vid(self):
		from urllib.parse import urlencode

		tgt_p = server.sys_root / server.prms['target']

		target_file_query = {
			'action': 'dl_vid',
			'auth': 'ftp',
			'dl_tgt': server.prms['target']
		}
		server.bin_jwrite({
			'status': ('lizard' if tgt_p.is_file() else 'fuckoff'),
			'cmd': f"""htbin/poolsys/poolsys.py?{urlencode(target_file_query)}"""
		})
		server.flush()



pool_sys = poolsys()

actions = md_actions(
	server,
	{
		'list_leagues': 			pool_sys.list_leagues,
		'list_league_matches': 		pool_sys.list_league_matches,
		'list_match_struct': 		pool_sys.list_match_struct,
		'list_media': 				pool_sys.list_media,
		'load_image_preview': 		pool_sys.load_image_preview,
		'load_fullres_pic': 		pool_sys.load_fullres_pic,
		'load_video_preview': 		pool_sys.load_video_preview,
		# 'generate_vid_preview': 	pool_sys.generate_vid_preview,
		'list_matches_w_subroot':	pool_sys.list_matches_w_subroot,
		'generate_webm_preview':	pool_sys.ensure_webm_generation,
		'get_webm':					pool_sys.get_webm,
		'get_webm_audio':			pool_sys.get_webm_audio,
		'check_webm_status':		pool_sys.check_webm_status,
		# 'resume_q':					pool_sys.mediaq.resume,
		'resume_q':					pool_sys.temp_resume_shit,


		# todo: temp here: download a video
		'get_dl_vid':				pool_sys.get_dl_vid,
		'dl_vid':					pool_sys.dl_vid
	}
)
actions.eval_action()
