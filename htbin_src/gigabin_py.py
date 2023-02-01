


# important todod: make this work with  with ... as
class gigabin:

	def __init__(self, src='', overwrite=False):
		from pathlib import Path
		import json, base64, os, sys
		self.giga_idn = 'gigachad'

		self.header = None
		self.bin = Path(src)

		# following 32 bytes after the identifier indicate the header length
		self.head_len = len(self.giga_idn) + 32

		# if the file does not exist and overwrite is false - error
		if not self.bin.is_file() and overwrite != True:
			raise Exception('File does not exist and overwrite is not True')

		# if overwrite is set to true, then overwrite existing/non existing file
		if overwrite == True:
			self.file_wipe()
			return

		# as of now it's either a valid gigabin or exception
		# todo: because of this check a file is being opened twice. Bad
		valid_fm = self.validate_format()
		if valid_fm != True:
			raise Exception('Given data structure does not represent a valid gigabin format')

		# giga read giga bin
		with open(str(src), 'rb') as chad:
			# move cursor to the end of the ID header
			chad.seek(len(self.giga_idn))
			# read 32 bytes of the header length
			head_size = int(chad.read(32).decode().replace('!', ''))
			chad.seek(0, os.SEEK_END)
			total_fsize = chad.tell()

			# read header
			chad.seek(total_fsize - head_size, 0)
			self.header = json.loads(base64.b64decode(chad.read(head_size)))


	# validate whether the file represents a valid giga bin or not
	def validate_format(self):
		tgt = Path(tgt)

		with open(str(tgt), 'rb') as chad:
			# first 8 bytes store the identifier
			given_id = chad.read(len(self.giga_idn)).decode()
			print('Validate Format', given_id)
			if given_id == self.giga_idn:
				return True
			else:
				return False

	# wipe the current file
	def file_wipe(self):
		if not self.bin.parent.is_dir():
			raise Exception('Parent directory of the target file (as well as the file itself) does not exist')

		self.header = {
			'stores': {},
			'version': '0.17',
			'total_size': None,
			'comment': ''
		}

		# create empty file 
		self.bin.write_text('')

		# init new file
		with open(str(self.bin), 'r+b') as chad:
			chad.write(self.giga_idn.encode())
			chad.write(('!'*32).encode())
			# create header
			empty_header = self.mkheader()
			# write header
			chad.write(self.mkheader())
			# write header length
			chad.seek(len(self.giga_idn))
			chad.write(str(len(empty_header)).encode())

		self.files = self.header['stores']

	# compile header into base64
	def mkheader(self):
		import base64
		import json
		return base64.b64encode(json.dumps(self.header).encode())


	# read a single bit
	# read as = json/bytes/text
	def read_solid(self, sname=None, read_as='bytes', missing_ok=False):
		import json
		# pathlib approach
		# specify missing_ok to ignore the fact that it's missing from the dictionary
		blocks = self.header['stores']
		tgt_block = blocks.get(sname)

		if not tgt_block and missing_ok != True:
			raise Exception('Requested block does not exist and missing_ok is not True')
		if not tgt_block and missing_ok == True:
			return

		bits = tgt_block['bits']

		with open(str(self.bin), 'rb') as chad:
			# skip header
			chad.seek(self.head_len, 0)
			# move to the offset of the requested file
			chad.seek(bits[0], 1)
			# read
			chunk = chad.read(bits[1])
			if read_as == 'bytes':
				return chunk
			if read_as == 'json':
				return josn.loads(chunk)
			if read_as == 'text':
				return chunk.decode()


	# read array-like
	def read_array(self, sname=None, read_as='bytes', missing_ok=False):
		import json
		# pathlib approach
		# specify missing_ok to ignore the fact that it's missing from the dictionary
		blocks = self.header['stores']
		tgt_array = blocks.get(sname)

		if not tgt_array and missing_ok != True:
			raise Exception('Requested array does not exist and missing_ok is not True')
		else:
			return

		bits = tgt_array['bits']

		with open(str(self.bin), 'rb') as chad:
			# yield bits one by one
			for bt in bits:
				# skip header
				chad.seek(self.head_len, 0)
				# move to the offset of the requested file
				chad.seek(bt[0], 1)
				# read
				chunk = chad.read(bt[1])
				if read_as == 'bytes':
					yield chunk
				if read_as == 'json':
					yield josn.loads(chunk)
				if read_as == 'text':
					yield chunk.decode()


	# Delete block or array
	def kill(self, sname=None):
		import os
		from pathlib import Path

		blocks = self.header['stores']
		tgt_block = blocks.get(sname)
		if not tgt_block:
			return

		original = open(str(self.bin), 'rb')
		temp_buffer = Path(f'{str(self.bin)}.buffer')
		temp_buffer.write_bytes(b'')
		target = open(str(temp_buffer), 'r+b')
		newhead = {
			'stores': {},
			'version': '0.17',
			'total_size': None,
			'comment': ''
		}

		# first write header preset
		target.write(self.giga_idn.encode())
		target.write(('!'*32).encode())

		# now write solid blocks
		for sld in blocks:
			# if it's solid and not requested deleteion name
			if blocks[sld]['type'] != 'solid' or sld == sname:
				continue

			src_bits = blocks[sld]['bits']

			#
			# read source block
			#

			# skip header
			original.seek(self.head_len, 0)
			# move cursor to target offset
			original.seek(src_bits[0], 1)
			# read chunk
			origin_chunk = original.read(src_bits[1])

			#
			# write this block to the new file
			#

			# write chunk info to the header
			newhead['stores'][sld] = {}
			print('rewrite', sld)
			newhead['stores'][sld]['type'] = 'solid'
			newhead['stores'][sld]['bits'] = (target.tell() - self.head_len, len(origin_chunk), None)
			# write chunk to the new file
			target.write(origin_chunk)

		original.close()


		#
		# then, write arrays
		#

		# todo: for now this uses the class method "read array"
		# which means that it will open/close the source file on each call
		for arr in blocks:
			# if it's array and not requested deleteion name
			if blocks[arr]['type'] != 'array' or arr == sname:
				continue

			# important todo: make the whole class work with with ... as
			# or at least open the file inside init and then reuse it

			# write chunk info to the header
			newhead['stores'][arr] = {}
			newhead['stores'][arr]['type'] = 'array'
			newhead['stores'][arr]['bits'] = []

			# iterate over array entries
			for ae in self.read_array(sname):
				# write chunk info
				newhead['stores'][arr]['bits'].append((target.tell() - self.head_len, len(ae), None))
				# write chunk to the new file
				target.write(ae)


		#
		# Finalize
		#

		# write down new header to the class storage
		self.header = newhead
		# collapse header into string
		mk_header = self.mkheader()

		# write header to file
		target.write(mk_header)

		# move cursor to the beginnig of the file
		target.seek(len(self.giga_idn), 0)
		# write header length
		target.write(str(len(mk_header)).encode())

		target.close()

		# rename shit
		self.bin.unlink(missing_ok=True)

		os.rename(str(temp_buffer), str(self.bin))


	# add solid block
	def add_solid(self, fname=None, data=None, overwrite=True, dohash=True):
		import os
		if None in (fname, data):
			raise Exception('Invalid info passed to add_solid')

		# if the name exists in the header, but overwrite is set to false
		# for now skip, later raise exception
		if fname in self.header['stores'] and overwrite != True:
			return False

		if fname in self.header['stores']:
			self.kill(fname)

		chad = open(str(self.bin), 'r+b')
		# chad.seek(0, os.SEEK_END)

		# erase exiting header and header length

		# erase header length
		chad.seek(len(self.giga_idn), 0)
		# get header length
		hlen = int(chad.read(32).decode().replace('!', ''))
		chad.seek(len(self.giga_idn), 0)
		# erase
		chad.write(('!'*32).encode())

		# erase header json
		chad.seek(hlen*(-1), os.SEEK_END)
		# erase
		chad.truncate()


		# update header before adding requested data
		self.header['stores'][fname] = {}
		self.header['stores'][fname]['type'] = 'solid'
		# eval hash, if asked
		p_hash = None
		if dohash == True:
			p_hash = self.eval_hash(data, 'sha256')
		self.header['stores'][fname]['bits'] = (chad.tell() - self.head_len, len(data), p_hash)

		# append requested data
		chad.write(data)

		# append header json
		mk_head = self.mkheader()
		chad.write(mk_head)

		# write header length
		chad.seek(len(self.giga_idn), 0)
		chad.write(str(len(mk_head)).encode())

		# close
		chad.close()










	# RAM-Efficient
	# applicable entries are: md5/sha256/sha512
	def hash_file(self, filepath=None, meth='md5', mb_read=100):
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
	# htype: md5/sha256/sha512
	def eval_hash(self, dt_input, htype='md5'):
		import hashlib

		if isinstance(dt_input, bytes):
			hasher = dt_input
		else:
			text = str(dt_input)
			hasher = text.encode()

		hash_obj = hashlib.md5(hasher)
		if htype == 'sha256':
			hash_obj = hashlib.sha256(hasher)
		if htype == 'sha512':
			hash_obj = hashlib.sha512(hasher)

		return hash_obj.hexdigest()











def mdma():
	from pathlib import Path
	thedir = Path(__file__).parent
	dicks = gigabin((thedir / 'ballsack.chad'), True)

	dicks.add_solid(
		'sex',
		'0123456789'.encode(),
		True
	)
	print('added sex', 'read:', dicks.read_solid('sex', 'text'))
	dicks.add_solid(
		'fuckoff',
		'-0_1_2_3_4_5_6_7_8_9-'.encode(),
		True
	)
	print('added fuckoff', 'read:', dicks.read_solid('fuckoff', 'text'))
	dicks.add_solid(
		'sex',
		'DICKSANDBALLS'.encode(),
		True
	)
	print('overwrote shite, read previously successfull read')
	print('read fuckoff:', dicks.read_solid('fuckoff', 'text'))












	return 
	(thedir / 'gigasex.chad').unlink(missing_ok=True)
	kurwa = gigabin(None, (thedir / 'gigasex.chad'))

	kurwa.add_file({
		'name': 'lizard',
		'data': '0_1_2_3_4_5_6_7_8_9'.encode(),
		'overwrite': True
	})
	kurwa.add_file({
		'name': 'sex',
		'data': 'POOTIS'.encode(),
		'overwrite': True
	})

	print(kurwa.read_file('lizard', 'text'))

	kurwa.delete_file(['sex'])

	sex = [
		r"C:\custom\vid_db\pin\glasgow.23_11_2022.23-45.mp4",
		r"C:\custom\vid_db\pin\bristol.17_09_2022.13-25.mp4",
		r"C:\custom\vid_db\pin\bigcity.19_03_2021.19-00.mp4"
	]

	print(kurwa.read_file('lizard', 'text'))

	for sid, nen in enumerate(sex):
		kurwa.add_file({
			'name': f'dicks{str(sid)}',
			'data': Path(nen).read_bytes(),
			'overwrite': False
		})

	for sid, nen in enumerate(sex):
		(thedir / f'balls{sid}.mp4').write_bytes(kurwa.read_file(f'dicks{str(sid)}', 'buffer'))


if __name__ == '__main__':
	mdma()