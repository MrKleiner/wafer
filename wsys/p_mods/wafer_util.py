
# =============================================
# 				Util finctions
# =============================================








# RAM-Efficient
# applicable entries are: md5/sha256/sha512
def hash_file(filepath=None, meth='md5', mb_read=100):
	import hashlib
	from pathlib import Path

	if filepath == None or not Path(filepath).is_file():
		return False

	file = str(filepath) # Location of the file (can be set a different way)

	# The size of each read from the file
	# default: 65535
	BLOCK_SIZE = (1024**2)*mb_read
	
	# Create the hash object, can use something other than `.sha256()` if you wish
	file_hash = hashlib.md5()
	if meth == 'sha256':
		file_hash = hashlib.sha256()
	if meth == 'sha512':
		file_hash = hashlib.sha512()
	if meth == 'sha1':
		file_hash = hashlib.sha1()

	with open(file, 'rb') as f: # Open the file to read it's bytes
		fb = f.read(BLOCK_SIZE) # Read from the file. Take in the amount declared above
		while len(fb) > 0: # While there is still data being read from the file
			file_hash.update(fb) # Update the hash
			fb = f.read(BLOCK_SIZE) # Read the next block from the file

	return(file_hash.hexdigest()) # Get the hexadecimal digest of the hash



# fast
# takes bytes or strings as an input
# hash 
# h: md5/sha256/sha512
def eval_hash(st, h='md5'):
	import hashlib

	if isinstance(st, bytes):
		hasher = st
	else:
		text = str(st)
		hasher = text.encode()

	hash_obj = hashlib.md5(hasher)
	if h == 'sha256':
		hash_obj = hashlib.sha256(hasher)
	if h == 'sha512':
		hash_obj = hashlib.sha512(hasher)
	if h == 'sha1':
		hash_obj = hashlib.sha1(hasher)

	return hash_obj.hexdigest()



# get evenly distributed points from a range
def even_points(low,up,leng):
	lst = []
	step = (up - low) / float(leng)
	for i in range(leng):
		lst.append(low)
		low = low + step
	return lst



# json with comments
# either takes bytes or path to the file
# default = path. Add True as a second param to eval json from passed bytes
def giga_json(inp, bt=False):
	import json
	from pathlib import Path

	if bt == True:
		jsb = inp
	else:
		jspath = Path(inp)
		if not jspath.is_file():
			raise Exception(f'Path passed to giga_json does not exist, {str(jspath)}')
		jsb = jspath.read_bytes()

	return json.loads(b'\n'.join([ln for ln in jsb.split(b'\n') if not ln.strip().startswith(b'//')]))



# generate random token
# pass True to generate a super long token (sha512)
# pass string 'short' to generate short
# bias is a multiplier for the random seed length. Defaults are good enough
def generate_token_v0(do_long=False, bias=1):
	from random import random
	if do_long == 'short':
		return eval_hash('!lizard?'.join([str(random()) for rnd in range(int(256*bias))]), 'sha1')
	if do_long == True:
		return eval_hash('!lizard?'.join([str(random()) for rnd in range(int(256*bias))]), 'sha512')
	else:
		return eval_hash('!lizard?'.join([str(random()) for rnd in range(int(64*bias))]), 'sha256')


# tlen is an int from 1 to 3
# 1: 32  chars / 128 bits / 16 bytes
# 2: 64  chars / 256 bits / 32 bytes (default)
# 3: 128 chars / 512 bits / 64 bytes

# bias is a paranoia level multiplier.
# int from 1 (default, good enough) to infinity (performance warning)

# tcrypto is whether to use crypto (slower, default) or pseudo (faster)
def generate_token(tlen=2, bias=1, tcrypto=True):
	if tcrypto == True:
		import secrets, hashlib
		if bias > 1:
			rndseed = secrets.token_bytes(int(64*bias))
			if tlen == 1:
				return hashlib.md5(rndseed).hexdigest()
			if tlen == 2:
				return hashlib.sha256(rndseed).hexdigest()
			if tlen == 3:
				return hashlib.sha512(rndseed).hexdigest()
		else:
			if tlen == 1:
				return secrets.token_hex(16)
			if tlen == 2:
				return secrets.token_hex(32)
			if tlen == 3:
				return secrets.token_hex(64)


		# default fallback
		return secrets.token_hex(32)


def sp_popen(exec_args):
	import subprocess as sp

	outp_data = None
	with sp.Popen(exec_args, stdout=sp.PIPE, bufsize=10**8) as sp_data_pipe:
		outp_data = sp_data_pipe.stdout.read()

	return outp_data

