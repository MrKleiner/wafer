import cgi, sys, cgitb
sys.path.append('..')
from server import server, md_actions
server = server(cgi, sys, cgitb)



class uploadsys:

	# basically auth
	def __init__(self):
		from pathlib import Path
		import json

		# destination directory to check auth against
		dest = server.sys_root / Path(server.prms['dest_dir'])

		# input user token
		usr_token = server.prms.get('auth')

		usr_alw = server.alw_db.db.get(usr_token)

		# no auth no shit
		if not usr_token or not usr_alw:
			server.bin_jwrite({'status': '1809246/ups/anything'})
			server.flush()

		# admin can upload anywhere
		if not 'admin' in usr_alw['admin']:
			# check league allowance
			if not dest.parent.parent.name in usr_alw['folders'] and not '%command' in usr_alw['folders']:
				server.bin_jwrite({'status': '1809246/ups/root'})
				server.flush()

			# now check whether allowed to upload to photos or moments
			if not dest.name in usr_alw['admin']:
				server.bin_jwrite({'status': '1809246/ups/struct'})
				server.flush()




	# this creates an empty file in the temp dir
	# and also creates an info object with the same id, but with different extension
	def init_lfs(self):
		# from pathlib import Path
		import json

		# first, generate a random id, aka Upload Token
		up_token = server.util.generate_token()

		# then, init the info object
		info_object = {
			'declared_size': server.prms['declare_size'],
			'declared_hash': server.prms['declare_hash'],
			'flname': server.prms['file_name'],
			'dest_dir': str(server.sys_root / server.prms['dest_dir']),
			'last_chunk_hash': None,
			'last_full_hash': None,
			# todo: also make it only accessible by the original uploader
			'upload_token': up_token
		}
		# create journal tasks
		fj = server.journal()

		# create empty target
		tgt_p = (server.tmp_dir / f'{up_token}.target')
		tgt_p.write_bytes(b'')
		fj.reg_file(tgt_p)
		# save info
		obj_p = (server.tmp_dir / f'{up_token}.object')
		obj_p.write_bytes(json.dumps(info_object).encode())
		fj.reg_file(obj_p)


		# return this object to client
		server.bin_jwrite({'status': 'created_target', 'token': up_token})
		server.flush()


	# add bytes to LFS
	def lfs_add(self):
		import json, time
		code_timings = time.time()

		lfs_tgt = server.tmp_dir / f"""{server.prms.get('upload_token')}.target"""

		# make sure that target exists
		# todo: specific error in case the info object is missing
		if not lfs_tgt.is_file():
			server.bin_jwrite({'status': '10092007', 'details': str(lfs_tgt)})
			server.flush()

		# get info object
		info_obj = json.loads(lfs_tgt.with_suffix('.object').read_bytes())

		# append bytes
		with open(str(lfs_tgt), 'ab') as lfs:
			lfs.write(server.bin)

		# save received chunk hash to info object
		info_obj['last_chunk_hash'] = server.util.eval_hash(server.bin, 'sha256')

		# now evaluate full hash
		# todo: why?
		# don't do this for now
		# info_obj['last_full_hash'] = server.util.hash_file(lfs_tgt, 'sha256')
		info_obj['last_full_hash'] = None

		server.bin_jwrite({
			'received_chunk_hash': info_obj['last_chunk_hash'],
			'full_hash': info_obj['last_full_hash'],
			'timings': time.time() - code_timings
		})
		server.flush()


	def lfs_collapse(self):
		import shutil, json, time

		code_timings = time.time()

		lfs_tgt = server.tmp_dir / f"""{server.prms.get('upload_token')}.target"""

		# make sure that target exists
		# todo: specific error in case the info object is missing
		if not lfs_tgt.is_file():
			server.bin_jwrite({'status': '10092007', 'details': str(lfs_tgt)})
			server.flush()

		# get info object
		info_obj = json.loads(lfs_tgt.with_suffix('.object').read_bytes())

		# if the destination exists already - return error
		# important todo: warn/ignore or overwrite ?
		dest_loc = (server.sys_root / info_obj['dest_dir'] / info_obj['flname'])
		dest_loc.unlink(missing_ok=True)
		# if dest_loc.is_file():
			# server.bin_jwrite({'status': 'error_dest_file_exists'})
			# server.flush()

		# move file to the destination
		shutil.move(str(lfs_tgt), str(dest_loc))

		# remove the info object
		lfs_tgt.with_suffix('.object').unlink(missing_ok=True)

		# important todo: there are way better places to do this...
		fj = server.journal()
		fj.process_jr()

		# return hash of the destination file
		server.bin_jwrite({
			'status': 'lizard',
			'server_checksum': server.util.hash_file(dest_loc, 'sha256'),
			'declared_checksum': info_obj['declared_hash'],
			'timings': time.time() - code_timings
		})
		server.flush()




uplsys = uploadsys()

actions = md_actions(
	server,
	{
		'init_lfs': 	uplsys.init_lfs,
		'lfs_add': 		uplsys.lfs_add,
		'lfs_collapse': uplsys.lfs_collapse
	}
)
actions.eval_action()