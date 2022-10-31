import cgi, sys, cgitb
sys.path.append('..')
from server import server, md_actions
server = server(cgi, sys, cgitb)

# important todo: https://trac.ffmpeg.org/wiki/Encode/VP9
class poolsys:

	def __init__(self):
		# import json
		# from pathlib import Path
		self.aa = 'aa'



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
		import shutil

		# target video filepath
		tgt_path = server.sys_root / Path(server.prms['video_path'])

		# if requested file is not of supported format - return error
		if not tgt_path.suffix.strip('.').lower() in server.allowed_vid:
			server.flush('Requested files does not match any supported video formats'.encode())
		
		# if this file exists in the previews pool - get it and return immediately
		preview_path = (tgt_path.parent / 'prdb_lzpreviews' / f'{tgt_path.name}.lzpreview.chad')
		if preview_path.is_file():
			server.x_files(preview_path, preview_path.name)

		# else - generate preview
		# create the folder with previews if it doesn't exist
		(tgt_path.parent / 'prdb_lzpreviews').mkdir(exist_ok=True)

		# start generating preview
		rum = self.generate_vid_preview(tgt_path)

		# unregister chad location
		# todo: not needed ?
		fj = server.journal()

		# move the preview to the previews folder
		newloc = tgt_path.parent / 'prdb_lzpreviews' / f'{tgt_path.name}.lzpreview.chad'
		shutil.move(str(rum), str(newloc))

		# unreg
		fj.unreg_file(rum)

		# send generated file to client
		server.x_files(newloc, newloc.name)




	def load_fullres_pic(self):
		# from pathlib import Path
		import os
		if os.stat(server.sys_root / server.prms['target']).st_size > ((1024**2)*50):
			return 'file is too big'.encode()

		server.x_files((server.sys_root / server.prms['target']), 'preview')


	# obvious todo: hardcoded 100 frames = bad
	# takes video path as an inout
	def generate_vid_preview(self, vidpath):
		import sys, json
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
		# first, get resolution and frame count of the video
		# ==========================================================

		# ffprobe.exe -v error -select_streams 0 -count_frames -show_entries stream=nb_read_frames,width,height -print_format json "C:\Users\baton\Downloads\hacker-1-5.mp4"
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

		# return path to the .chad file
		return chad_location



	# this is the only obvious way of doing this
	# aka calling this from js and not waiting for it to return anything
	def generate_webm_preview(self):
		import subprocess as sp

		# get path to the video
		vid_path = server.sys_root / server.prms.get('vidpath')
		# output dir is the lzpreviews folder
		preview_path = vid_path.parent / 'prdb_lzpreviews' / f'{vid_path.name}.fullvidp.lzpreview.webm'

		# create ffmpeg params
		ffmpeg_prms = [
			# ffmpeg executable
			r'/usr/bin/ffmpeg',

			# automatically discard if file exists
			'-n',

			# input file
			'-i', str(vid_path),

			# filters: clamp to width
			'-vf', r'scale=w=min(iw\\,420):h=-2',

			# audio
			'-acodec', 'libopus',
			'-b:a', '96k',

			# video encoding shit
			'-c:v', 'libvpx-vp9',
			'-minrate', '50k',
			'-b:v', '120k',
			'-maxrate', '700k',

			# output file location
			str(preview_path)
		]

		# захуярь раммштайн
		sp.Popen(ffmpeg_prms)

		# flush the shit
		server.flush('ok'.encode())











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
		'list_matches_w_subroot':	pool_sys.list_matches_w_subroot
		'generate_webm_preview':	pool_sys.generate_webm_preview
	}
)
actions.eval_action()
