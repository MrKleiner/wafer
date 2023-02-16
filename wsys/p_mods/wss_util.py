
# I fucking hate WebSockets
# CAN YOU JUST SEND THE FUCKING PAYLOAD LENGTH THROUGH BYTES???
# WHY THE FUCK IS IT IN SEQUENTIAL BITS ???


# Every WSS session starts with js sending a handshake request to the server
# This function will process the handshake and return a response
def eval_handshake(hshake):
	import hashlib, base64
	lines = hshake.decode().split('\r\n')
	del lines[0]
	hshake_info = {}
	for ln in lines:
		splitline = ln.split(': ')
		hshake_info[splitline[0].strip()] = ': '.join(splitline[1:]).strip()

	print(json.dumps(hshake_info, indent=4))

	if not 'Sec-WebSocket-Key' in hshake_info:
		return False

	resolve = {
		'Upgrade': 'websocket',
		'Connection': 'Upgrade',
		'Sec-WebSocket-Accept': base64.b64encode(hashlib.sha1((hshake_info['Sec-WebSocket-Key'] + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11').encode()).digest()).decode()
	}

	rsp = 'HTTP/1.1 101 Switching Protocols\r\n'

	for key in resolve:
		rsp += f"""{key}: {resolve[key]}\r\n"""

	rsp += '\r\n'

	print(rsp)

	return rsp.encode()

# Decode the incoming data
# Every chunk is masked and therefore has to be unmasked
# The mask is stored in the frame
def unmask(dmask, dbytes):
	dc = []
	for j, bt in enumerate(dbytes):
		dc.append(bt ^ dmask[j%4])
	return bytes(dc)


# After establishing the handshake - 
# Each data bundle starts with a header with some mask info n shit
def frame_decode(data):
	frame = bytearray(data)

	length = frame[1] & 127

	indexFirstMask = 2
	if length == 126:
		indexFirstMask = 4
	elif length == 127:
		indexFirstMask = 10

	indexFirstDataByte = indexFirstMask + 4
	mask = frame[indexFirstMask:indexFirstDataByte]

	i = indexFirstDataByte
	j = 0
	decoded = []
	while i < len(frame):
		decoded.append(frame[i] ^ mask[j%4])
		i += 1
		j += 1

	# return "".join(chr(byte) for byte in decoded)
	return (bytes(decoded), mask)


# some bindings and shortcuts
class wss_frame:
	"""Easier frame evaluation"""
	def __init__(self, arg):
		self.arg = 'wss'
		







