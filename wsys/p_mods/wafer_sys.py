

def wf_socket_server(room_callback):







# srv_cfg = Server Config
def uploadsys_gateway(srv_cfg):
	server_info = srv_cfg





def watchdogs_gateway(srv_cfg):
	import socket
	server_info = srv_cfg

	# Port to run the server on
	port = int(server_info['watchdogs_port'])
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




