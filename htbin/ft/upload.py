import cgi, sys, cgitb
sys.path.append('..')
from server import server, md_actions
server = server(cgi, sys, cgitb)







class imaliar:
	# sorry...
	# WILL FIX ASAP !!!!!!!!!!!!!!
	def __init__(self, prms={}, dt='', sv={}):
		import json
		from pathlib import Path

		self.prms = prms
		self.bin = dt
		self.server = sv
		self.sysroot = Path(json.loads((sv['root'] / 'db' / 'root.json').read_bytes())['root_path'])

		# todo: this is something that has to be globally available
		self.allowed_vid = [
			'mp4',
			'mov',
			'webm',
			'ts',
			'mts',
			'mkv',
			'avi'
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
			'hdr'
		]


	@property
	def accept_file(self):
		from pathlib import Path
		import json
		# this is literally 0.01% of what was promised...
		# FOR NOW !!!!!!!!!!!!
		# this is why it's a class and not a lonely function
		# for now there has to be an illusion of working shit
		# but THEN, a REAL deal would begin...
		dest = Path(self.prms['dest'])

		# important todo: this is a dirty auth
		# dirty because it doesn't check whether it's the subfolder of the match struct

		# no auth no shit
		if not self.server['auth_cl']:
			return json.dumps({'status': '1809246/anything'})

		# admin can upload wherever
		if not 'admin' in self.server['auth_cl']['admin']:
			# check league allowance
			if dest.parent.parent.parent.name in self.server['auth_cl']['folders'] or '%command' in self.server['auth_cl']['folders']:
				pass
			else:
				return json.dumps({'status': '1809246/root'})

			# now check whether allowed to upload to photos or moments
			if not dest.parent.name in self.server['auth_cl']['admin']:
				return json.dumps({'status': '1809246/struct'})

		(self.sysroot / str(dest)).write_bytes(self.bin)
		return json.dumps({'status': 'lizard', 'dst_name': dest.name})



	@property
	# init new LFS file in the temp dir
	def lfs_create(self):
		from pathlib import Path
		import json, sys, random
		sys.path.append('.')
		from util import eval_hash

		# only allow this if user actually has the rights to write to the final dir
		filedest = Path(self.prms['file_dest'])

		# important todo: this is a dirty auth
		# dirty because it doesn't check whether it's the subfolder of the match struct

		# no auth no shit
		if not self.server['auth_cl']:
			return json.dumps({'status': '1809246/anything'})

		# admin can upload wherever
		if not 'admin' in self.server['auth_cl']['admin']:
			# check league allowance
			if filedest.parent.parent.parent.name in self.server['auth_cl']['folders'] or '%command' in self.server['auth_cl']['folders']:
				pass
			else:
				return json.dumps({'status': '1809246/lfs/root'})

			# now check whether allowed to upload to photos or moments
			if not filedest.parent.name in self.server['auth_cl']['admin']:
				return json.dumps({'status': '1809246/struct'})

		# create random name
		seed = str(random.random()) + str(random.random()) + str(random.random())
		super_token = eval_hash(seed, 'sha256')

		# with open('pissoff.shit', 'r+b') as f:

		# init empty file
		tmp_loc_path = Path(self.server['cfg']['preview_db']) / 'temp_shite' / f"""{super_token}.{self.prms['flname']}"""
		tmp_loc_path.write_bytes(b'')

		# return target
		return json.dumps({'status': 'ok', 'target': str(tmp_loc_path)})


	# add to previously created lfs object
	@property
	def lfs_append(self):
		import json
		from pathlib import Path
		tmp_loc_path = Path(self.server['cfg']['preview_db']) / 'temp_shite' / self.prms['target']
		
		if not tmp_loc_path.is_file():
			return json.dumps({'status': 'error', 'reason': 'target does not exist...'})

		with open(str(tmp_loc_path), 'ab') as f:
			f.write(self.bin)

		return json.dumps({'status': 'ok'})


	# stop writing and move to target dir
	@property
	def lfs_collapse(self):
		import json, shutil
		from pathlib import Path

		target_dir = Path(self.prms['tgt_dir'])
		src_lfs = Path(self.prms['src_lfs'])
		tmp_loc_path = Path(self.server['cfg']['preview_db'])

		if (tmp_loc_path / 'temp_shite' / src_lfs).is_file():
			remove_token = src_lfs.name.split('.')
			del remove_token[0]
			shutil.move(str(tmp_loc_path / 'temp_shite' / src_lfs), str(self.sysroot / target_dir / '.'.join(remove_token)))
			return json.dumps({'status': 'ok'})
		else:
			return json.dumps({'status': 'erro', 'reason': 'source file does not exist'})




class uploadsys:

	# basically auth
	def __init__(self):
		from pathlib import Path
		import json

		# destination directory to check auth against
		dest = Path(server.prms['dest_dir'])

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
			'dest_dir': server.prms['dest_dir'],
			'last_chunk_hash': None,
			'last_full_hash': None,
			# todo: also make it only accessible by the original uploader
			'upload_token': up_token
		}
		# create empty target
		(server.tmp_dir / f'{up_token}.target').write_bytes(b'')
		# save info
		(server.tmp_dir / f'{up_token}.object').write_bytes(json.dumps(info_object).encode())

		# return this object to client
		server.bin_jwrite({'status': 'created_target', 'token': up_token})
		server.flush()


	# add bytes to LFS
	def lfs_add(self):
		import json

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
		info_obj['last_full_hash'] = server.util.hash_file(lfs_tgt, 'sha256')

		server.bin_jwrite({
			'received_chunk_hash': info_obj['last_chunk_hash'],
			'full_hash': info_obj['last_full_hash']
		})
		server.flush()


	def lfs_collapse(self):
		import shutil, json

		lfs_tgt = server.tmp_dir / f"""{server.prms.get('upload_token')}.target"""

		# make sure that target exists
		# todo: specific error in case the info object is missing
		if not lfs_tgt.is_file():
			server.bin_jwrite({'status': '10092007', 'details': str(lfs_tgt)})
			server.flush()

		# get info object
		info_obj = json.loads(lfs_tgt.with_suffix('.object').read_bytes())

		# if the destination exists already - return error
		dest_loc = (server.sys_root / info_obj['dest_dir'] / info_obj['flname'])
		if dest_loc.is_file():
			server.bin_jwrite({'status': 'error_dest_file_exists'})
			server.flush()

		# move file to the destination
		shutil.move(str(lfs_tgt), str(dest_loc))

		# remove the info object
		lfs_tgt.with_suffix('.object').unlink(missing_ok=True)

		# return hash of the destination file
		server.bin_jwrite({
			'status': 'lizard',
			'server_checksum': server.util.hash_file(dest_loc, 'sha256'),
			'declared_checksum': info_obj['declared_hash']
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