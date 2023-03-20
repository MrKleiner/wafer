import sys
sys.path.append('..')
from server import server, jateway
server = server()



class uploadsys:

	# basically auth
	def __init__(self):
		from pathlib import Path
		import json



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





	#
	# new system
	#

	# todo: should it actually be a POST request ?
	# params:
	# declared_size
	# declared_hash
	# dest_dir
	# file_name
	# chunk_size
	# declared_chunks

	# todo: ensure there are no random token collisions
	# one way to do it is insert a predefined amount of additional characters at random points in the id
	def create_target(self):
		import sqlite3, datetime
		json = server.json
		fj = server.journal()

		target_dest = Path(server.prms['dest_dir']) / server.prms['file_name']

		# first, check if user is allowed to upload to the destination
		if not server.wfauth.resolve_path(target_dest):
			server.flush_json({
				'status': 'insufficient_rights',
				'details': f'This user is not allowed to write to the target destination: {str(target_dest)}'
			})

		# now check if the destination dir exists
		# this is done AFTER the auth check
		# to prevent "probing"
		# aka checking which folders/files exist by observing the access denial
		if not (server.ftp_root / target_dest).parent.is_dir():
			server.flush_json({
				'status': 'invalid_destination',
				'details': f'The destination folder does not exist: {str(target_dest)}'
			})

		# now, generate a random id, aka Upload Token
		up_token = server.util.generate_token()

		# create the info object
		info_object = {
			# database record
			'uploader': server.wfauth.userid,
			'flname': str(target_dest.name),
			'dest_dir': str(target_dest.parent),
			# todo: also make it only accessible by the original uploader
			'upload_token': up_token,
			'declared_hash': server.prms['declared_hash'],

			# additional info
			'declared_size': server.prms['declared_size'],
			'last_chunk_hash': None,
			'chunk_size': server.prms['chunk_size'],
			'declared_chunk_count': server.prms['declared_chunks'],
			'last_chunk_index': 0,
		}

		# now create the database record
		connection = sqlite3.connect(str(server.authdb_path / 'authsys' / 'users' / 'uploads.wft'))
		cursor_obj = connection.cursor()

		params = ("""
			INSERT INTO uploads
			(user_id, dest, init_time, token, declared_hash)
			VALUES (?, ?, ?, ?, ?);
		""")

		data_tuple = (
			info_object['uploader'],
			str(target_dest),
			datetime.datetime.now(),
			info_object['upload_token'],
			server.prms['declared_hash'],
		)
		cursor_obj.execute(params, data_tuple)
		connection.commit()
		connection.close()

		# now dump the info object into the uploads dir

		# create empty target
		target_path = (server.sysdb_path / 'uploads' / f'{up_token}.target')
		target_path.write_bytes(b'')
		fj.reg_file(target_path, 12)
		# save info
		object_path = (server.sysdb_path / 'uploads' / f'{up_token}.object')
		object_path.write_bytes(json.dumps(info_object).encode())
		fj.reg_file(object_path, 12)
		# register chunks file for deletion
		# chunk file stores sha256 hex hash of each chunk separated by line breaks
		fj.reg_file(object_path.with_suffix('.chunks'), 12)

		# return the object to client
		server.flush_json({'status': 'created_target', 'token': up_token})


	def target_append(self):

		tgt_path = server.sysdb_path / 'uploads' / f"""{server.prms.get('upl_token')}.target"""

		# first make sure that target exists
		# todo: specific error in case the info object is missing
		if not tgt_path.is_file():
			server.fatal_error('no_target_found')
			server.flush_json({
				'success': False,
				'error_id': '10092007',
				'details': f"""Cannot find a .target file with the specified upload token: {str(tgt_path)}"""
			})

		# get info object
		info_obj = server.json.loads(tgt_path.with_suffix('.object').read_bytes())

		# now compare declared hash and what server received
		# if it doesn't match - abort
		# this could happen when the connection was aborted in the middle of the chunk transfer
		received_chunk_hash = server.util.eval_hash(server.bin, 'sha256')

		if received_chunk_hash != server.prms.get('declared_hash'):
			server.fatal_error('hash_mismatch')
			server.flush_json({'error_id': '4600', 'details': f"""The received data hash does not match the declared one"""})

		# append bytes
		with open(str(tgt_path), 'ab') as target:
			target.write(server.bin)

		# update info object
		info_obj['last_chunk_hash'] = received_chunk_hash

		# update chunks file
		with open(str(tgt_path.with_suffix('.chunks')), 'a') as chunks:
			chunks.write(received_chunk_hash + '\n')

		server.flush_json({
			'received_chunk_hash': info_obj['last_chunk_hash']
		})


	def upload_collapse(self):
		pass


	def continue_from_chunk_id(self):

		tgt_path = server.sysdb_path / 'uploads' / f"""{server.prms.get('upl_token')}.target"""

		# first make sure that target exists
		# todo: specific error in case the info object is missing
		# todo: separate this into a separate function
		if not tgt_path.is_file():
			server.fatal_error('no_target_found')
			server.flush_json({
				'success': False,
				'error_id': '10092007',
				'details': f"""Cannot find a .target file with the specified upload token: {str(tgt_path)}"""
			})

		# get info object
		info_obj = server.json.loads(tgt_path.with_suffix('.object').read_bytes())

		server.flush_json(info_obj)



uplsys = uploadsys()

actions = md_actions(
	server,
	{
		'init_lfs': 	uplsys.init_lfs,
		'lfs_add': 		uplsys.lfs_add,
		'lfs_collapse': uplsys.lfs_collapse
	}
)
# actions.eval_action()