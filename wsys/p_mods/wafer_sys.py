
class wfcfg_ctrl:
	"""Easier access to configs and sys structure"""
	def __init__(self, cfgdir, sysroot):
		import json
		from pathlib import Path
		self.json = json
		self.Path = Path
		self.cfgdir = Path(cfgdir)
		self.sysroot = sysroot
		self.wsys_dir = sysroot / 'wsys'
		self.webcl_dir = sysroot / 'web'
		self.syslog_dir = sysroot / 'wsys' / 'syslog'


	def __getitem__(self, cfgname):
		return json.loads((self.cfgdir / f'{cfgname}.lzrd').read_bytes())



class wf_sys_util:
	"""Sys utils, like logging. Not to be confused with wafer_util"""
	def __init__(self, cfgctrl):
		self.cfgctrl = cfgctrl

	def syslog(self, logname='a', logtext='a'):
		try:
			tgt_file = self.syslog_dir / f'{logname}.lzlog'
			# todo: assign free id
			try:
				tgt_file.write_bytes(logtext)
			except Exception as e:
				tgt_file.write_text(str(logtext))
		except Exception as e:
			return False

		








def wf_socket_server(room_callback):







# srv_cfg = Server Config
def uploadsys_gateway(cfgctrl):
	# server_info = srv_cfg





def watchdogs_gateway(cfgctrl):
	import socket
	# server_info = srv_cfg

	# Port to run the server on
	port = int(cfgctrl['sysc_base']['watchdogs_port'])
	# Create the Server object
	s = socket.socket()
	# Bind server to the specified port. 0 = Find the closest free port and run stuff on it
	s.bind(('localhost', port))
	# Basically launch the server
	# The number passed to this function identifies the max amount of simultaneous connections
	# If the amount of connections exceeds this limit - connections become rejected till other ones are resolved (aka closed)
	# 0 = infinite
	s.listen(19)

	print('Server listening on port', s.getsockname()[1])

	# (thisdir / 'prt.sex').write_text(str(s.getsockname()[1]))

	while True:
		print('Entering the main listen cycle which would spawn rooms upon incoming connection requests...')
		# Try establishing connection, nothing below this line would get executed
		# until server receives a new connection
		conn, address = s.accept()
		print('Got connection, spawning a room. Client info:', address)
		# newroom = threading.Thread(target=room, args=(conn, address)).start()
		process = multiprocessing.Process(target=room, args=(conn, address, resps,))
		process.daemon = True
		process.start()
		print('Spawned a room, continue accepting new connections')




