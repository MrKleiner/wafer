
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
# default = path. Add True as a second param to eval json bytes
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
def generate_token(do_long=False):
	from random import random
	if do_long == True:
		return eval_hash('!lizard?'.join([str(random()) for rnd in range(128)]), 'sha512')
	else:
		return eval_hash('!lizard?'.join([str(random()) for rnd in range(64)]), 'sha256')
