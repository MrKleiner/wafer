import sys
sys.path.append('..')
from server import server, jateway
server = server()









# This is responsible for precessing the media preview generation queue
# Obsolete
class mqueue:
	def __init__(self):

		# init the mediagen class
		# (that class is a set of functions which generate actual previews n shit)
		self.mgen = media_gen()

		# store possible actions
		self.actions = {
			'webm':				self.mgen.generate_webm_preview,
			'frame_preview':	self.mgen.generate_vid_preview
		}

		# shortcut to the queue folder
		self.qdb = server.sysdb_path / 'preview_queue'

		# ensure that the preview queue folder exists
		self.qdb.mkdir(exist_ok=True)

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
			# and that this parameter is an input file path to the task description
			self.actions[task_d['task']](inp_loc)

			# once done with the action - delete the task file
			current_item.unlink(missing_ok=True)




		# once done with the queue - remove the lock file
		q_lock_file.unlink(missing_ok=True)
		# and uregister it from the journal
		fj.unreg_file(q_lock_file)

		server.flush('kill linux'.encode())

	# add an item to the registry
	# takes the path of the target video
	# and the task type
	# important todo: for now the target path is also an id of the task
	def reg_item(self, tgt_path, tsk):
		import json
		from datetime import datetime

		tm = datetime.now().timetuple()
		rg_info = json.dumps({
			'input': str(tgt_path),
			'output': None,
			'task': str(tsk),
			'timestamp': '-'.join([str(tm.tm_year), str(tm.tm_mon), str(tm.tm_mday), str(tm.tm_hour), str(tm.tm_min)])
		})

		# task id (filename inside the task pool) is filepath relative to ftp root + --task_type--
		task_id = server.util.eval_hash(f'{str(tgt_path)}--{str(tsk)}--', 'sha256')
		# if this task exists already - don't do shit
		tfile_path = self.qdb / f'{task_id}.qi'
		if tfile_path.is_file():
			return 'task exists'

		# else - add it to the registry
		(self.qdb / f'{task_id}.qi').write_bytes(rg_info.encode())
		return 'registered a new task'


	# read queue into a json
	def list_queue(self):
		import json
		tasks = []
		for qi in self.qdb.glob('*.qi'):
			tsk = json.loads(qi.read_bytes())
			tsk['task_id'] = qi.stem
			tasks.append(tsk)
		server.bin_jwrite(tasks)
		server.flush()


# important todo: https://trac.ffmpeg.org/wiki/Encode/VP9
class poolsys:

	def __init__(self):
		# import json
		# from pathlib import Path
		# self.mediaq = mqueue()


	def list_dir(self):
		import json, os
		# todo: server already has pathlib
		from pathlib import Path

		matches = []

		for match in (server.ftp_root / Path(server.prms['target']).resolve(strict=False)).glob('*'):

			# admins are allowed to view anything
			if not server.wfauth.resolve_path(match) and not server.wfauth.isadmin:
				continue

			if not match.is_dir():
				fl_info = {
					'lfs': (True if os.stat(str(match)).st_size >= ((1024**2)*3) else False),
					'stats': f"""{((1024**2)*3)}/{os.stat(str(match)).st_size}""",
					'etype': 'file',
					'path': str(match.relative_to(server.ftp_root)),
					'flname': match.name
				}

				if match.suffix.strip('.').lower() in server.allowed_vid:
					fl_info['etype'] = 'vid'
				if match.suffix.strip('.').lower() in server.allowed_img:
					fl_info['etype'] = 'img'
			else:
				fl_info = {
					'lfs': False,
					'stats': '0/0',
					'etype': 'dir',
					'dirname': match.name
				}


			matches.append(fl_info)


		server.bin_jwrite(matches)
		server.flush()


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
		webp = self.mgen.generate_pic_preview(tgt_path)

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
		'list_dir': 				pool_sys.list_dir,
		'load_image_preview': 		pool_sys.load_image_preview,
		'load_fullres_pic': 		pool_sys.load_fullres_pic,
		'load_video_preview': 		pool_sys.load_video_preview,
		# 'generate_vid_preview': 	pool_sys.generate_vid_preview,
		# 'list_matches_w_subroot':	pool_sys.list_matches_w_subroot,
		'generate_webm_preview':	pool_sys.ensure_webm_generation,
		'get_webm':					pool_sys.get_webm,
		'get_webm_audio':			pool_sys.get_webm_audio,
		'check_webm_status':		pool_sys.check_webm_status,
		# 'resume_q':					pool_sys.mediaq.resume,
		'resume_q':					pool_sys.temp_resume_shit,

		# debug queue lister
		'list_q':					pool_sys.mediaq.list_queue,

		# todo: temp here: download a video
		'get_dl_vid':				pool_sys.get_dl_vid,
		'dl_vid':					pool_sys.dl_vid
	}
)
actions.eval_action()
