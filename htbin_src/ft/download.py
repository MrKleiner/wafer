import sys
sys.path.append('..')
from server import server, jateway
server = server()



class download_sys:

	# basically auth
	def __init__(self):
		self.sex = 'lizards'


	# download many files as zip
	def create_zip(self):
		from zipfile import ZipFile
		from urllib.parse import urlencode
		import json
		# zip.write(str(file), Path(file).name)

		# create a list of files to zip
		# keep in mind that input file paths are relative to the FTP root
		input_flist = [(server.sys_root / fl) for fl in json.loads(server.bin)]

		# add files one by one to the zip archive

		# todo: generate hash of file paths and use it as the zip name
		# to avoid generating duplicate zips
		zip_token = server.util.generate_token()
		zip_path = server.tmp_dir / f'{zip_token}.zip'
		with ZipFile(str(zip_path), 'w') as zip:
			for file in input_flist:
				zip.write(file, file.name)

		# very important: register for deletion
		fj = server.journal()
		fj.reg_file(zip_path)

		# send back query required to download the file
		target_file_query = {
			'action': 'dl_zip',
			'auth': 'ftp',
			'dl_tgt': f'{zip_token}.zip'
		}
		server.bin_jwrite({
			'status': 'lizard',
			'cmd': f"""htbin/ft/download.py?{urlencode(target_file_query)}"""
		})
		server.flush()

	# download existing zip payload
	def dl_zip(self):
		server.x_files((server.tmp_dir / server.prms.get('dl_tgt')), 'photos.zip')



dlsys = download_sys()

actions = md_actions(
	server,
	{
		'create_zip': dlsys.create_zip,
		'dl_zip': dlsys.dl_zip
	}
)
actions.eval_action()