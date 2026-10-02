import json
import uuid
import hashlib
import math
import contextlib

from pathlib import Path

from .wafer_util import *






class WaferFileUploadChunkWriter(NamedPrint):
	def __init__(self, chunk_size, chunk_fpath, declared_hash_hex):
		self.chunk_size = chunk_size
		self.chunk_fpath = chunk_fpath
		self.declared_hash_hex = declared_hash_hex

		self.written_bytes_hash = None
		self.written_bytes_len = None

		self.fbuf = None

	def __enter__(self):
		self.written_bytes_hash = hashlib.sha256()
		self.written_bytes_len = 0

		self.chunk_fpath.unlink(missing_ok=True)

		self.fbuf = open(self.chunk_fpath, 'wb')
		self.fbuf.write(
			bytes.fromhex(self.declared_hash_hex)
		)

		return self.add_bytes

	def __exit__(self, e_type, e_val, e_trace):
		self.fbuf.close()

		if e_type:
			self.chunk_fpath.unlink(missing_ok=True)
			return

		if self.written_bytes_hash.hexdigest() != self.declared_hash_hex:
			self.chunk_fpath.unlink(missing_ok=True)
			raise ValueError(
				'FATAL: Hash mismatch'
			)

	def add_bytes(self, tgt_bytes):
		self.written_bytes_len += len(tgt_bytes)
		if self.written_bytes_len > self.chunk_size:
			raise ValueError(
				f'Chunk size of len {self.written_bytes_len} '
				f'exceeds the declared chunk size of {self.chunk_size}'
			)

		self.written_bytes_hash.update(tgt_bytes)
		self.fbuf.write(tgt_bytes)



class WaferFileUploadChunkInstance(NamedPrint):
	def __init__(self, chunk_array, chunk_index):
		self.chunk_array = chunk_array
		self.chunk_index = int(chunk_index)
		self.chunk_fpath = self.chunk_array.chunks_dir / str(self.chunk_index)

		self._is_alright = None
		self._file_exists = None
		self._hash_matches = None

	@property
	def file_exists(self):
		if self._file_exists != None:
			return self._file_exists

		self._file_exists = self.chunk_fpath.is_file()

		return self._file_exists

	@property
	def hash_matches(self):
		if self._hash_matches != None:
			return self._hash_matches

		if not self.file_exists:
			self._hash_matches = False
			return self._hash_matches

		with open(self.chunk_fpath, 'rb') as fbuf:
			if len(declared_hash := fbuf.read(32)) != 32:
				self._hash_matches = False
				return self._hash_matches

			written_hash = hashlib.sha256()

			while (chunk := fbuf.read(8192)):
				written_hash.update(chunk)

			if written_hash.digest() == declared_hash:
				self._hash_matches = True

		return self._hash_matches

	@property
	def is_alright(self):
		if self._is_alright != None:
			return self._is_alright

		self._is_alright = self.hash_matches

		return self._is_alright

	def write(self, declared_hash_hex):
		self._is_alright = None
		self._file_exists = None
		self._hash_matches = None

		return WaferFileUploadChunkWriter(
			self.chunk_array.chunk_size,
			self.chunk_fpath,
			declared_hash_hex,
		)

	@contextlib.contextmanager
	def real_fbuf(self):
		fbuf = open(self.chunk_fpath, 'rb')
		fbuf.read(32)

		try:
			yield fbuf
		finally:
			fbuf.close()



class WaferFileUploadChunkArray(NamedPrint):
	def __init__(self, upload_instance, chunks_dir, chunk_size, chunk_amount):
		self.upload_instance = upload_instance

		self.chunks_dir = chunks_dir
		self.chunk_size = chunk_size
		self.chunk_amount = chunk_amount

	def place(self, chunk_index, declared_hash_hex):
		if chunk_index > (self.chunk_amount - 1):
			raise ValueError(
				f'Chunk with index {chunk_index} '
				f'is outside of declared bounds {self.chunk_amount}'
			)

		self.upload_instance.info_data['last_chunk_index'] = chunk_index

		chunk_instance = WaferFileUploadChunkInstance(
			self,
			chunk_index,
		)

		if chunk_instance.file_exists:
			raise ValueError(
				f'Chunk at index {chunk_index} already exists. '
				'It can only be modified. NOT created'
			)

		return chunk_instance.write(declared_hash_hex)

	def calc_resume_chunk(self):
		present_chunk_amount = len(list(
			i for i in self.chunks_dir.glob('*')
		))

		# No chunks present - resume from beginning
		if not present_chunk_amount:
			return WaferFileUploadChunkInstance(
				self, 0
			)

		# Some amount of chunks present.
		# Check the last one and see if it's alright.
		# If not - resume from it
		chunk_instance = WaferFileUploadChunkInstance(
			self,
			present_chunk_amount - 1
		)
		if not chunk_instance.is_alright:
			return chunk_instance

		# Last chunk is alright - check if max chunks reached.
		# If so - nothing to resume from
		if self.chunk_amount == present_chunk_amount:
			return None

		# Otherwise - resume from next (not yet existing) chunk
		return WaferFileUploadChunkInstance(
			self,
			present_chunk_amount,
		)

	def calc_missing_chunks(self, limit=1337):
		missing_chunks = []

		for chunk_idx in range(self.chunk_amount):
			chunk_instance = WaferFileUploadChunkInstance(
				self,
				chunk_idx,
			)

			if not chunk_instance.file_exists:
				missing_chunks.append(chunk_instance)

			if len(missing_chunks) > limit:
				break

		return missing_chunks

	def calc_broken_chunks(self, limit=1337):
		broken_chunks = []

		for chunk_idx in range(self.chunk_amount):
			chunk_instance = WaferFileUploadChunkInstance(
				self,
				chunk_idx,
			)

			if not chunk_instance.is_alright:
				broken_chunks.append(chunk_instance)

			if len(broken_chunks) > limit:
				break

		if broken_chunks:
			self.consume_retry()

		return broken_chunks

	def collapse_into(self, fpath):
		present_chunk_amount = len(list(
			i for i in self.chunks_dir.glob('*')
		))

		if present_chunk_amount != self.chunk_amount:
			raise ValueError(
				'Upload is unfinished OR fucked: '
				f'Present chunk amount: {present_chunk_amount}, '
				f'declared chunk amount: {self.chunk_amount}'
			)

		fpath.unlink(missing_ok=True)

		with open(fpath, 'wb') as fbuf:
			for chunk_idx in range(self.chunk_amount):
				chunk_instance = WaferFileUploadChunkInstance(
					self,
					chunk_idx
				)

				if not chunk_instance.is_alright:
					raise ValueError(
						f'Cannot collapse: Faulty chunk at index {chunk_idx}'
					)

				with chunk_instance.real_fbuf() as chunk_fbuf:
					while (chunk := chunk_fbuf.read(8192)):
						fbuf.write(chunk)

	def consume_retry(self):
		self.upload_instance.info_data['last_chunk_retry_amount'] += 1
		self.upload_instance.save_info()

	def reset_retries(self):
		self.upload_instance.info_data['last_chunk_retry_amount'] = 0
		self.upload_instance.save_info()



class WaferFileUploadInstance(NamedPrint):
	DEFAULT_CHUNK_SIZE_MB = (1024**2) * 10
	DEFAULT_MAX_RETRIES = 69

	def __init__(self, uploads_dir, upload_id):
		self.uploads_dir = uploads_dir
		self.upload_id = str(upload_id)

		self.root_dir = self.uploads_dir / self.upload_id

		self._chunks_dpath = None
		self._info_fpath = None

		self._info_data = None

		self._chunk_size = None
		self._chunk_amount = None

		self._chunk_array = None

	@classmethod
	def alloc(cls, uploads_dir, file_size, chunk_size=None):
		for i in range(500):
			upload_instance = cls(
				uploads_dir,
				uuid.uuid4(),
			)
			if not upload_instance.root_dir.is_dir():
				upload_instance.root_dir.mkdir()
				break
		else:
			cls.nprint(
				'FATAL GLOBAL SYS FAIL: '
				'Failed to generate random dir name for a file upload'
			)
			return False

		with upload_instance.info_data.edit() as info_data:
			info_data['chunk_size'] = max(
				(chunk_size or cls.DEFAULT_CHUNK_SIZE_MB),

				# Has to be any positive int
				8192
			)

			info_data['chunk_amount'] = max(
				math.ceil(
					file_size / (chunk_size or cls.DEFAULT_CHUNK_SIZE_MB)
				),

				# Make sure it's not negative
				0
			)

		return upload_instance

	@classmethod
	def retrieve(cls, uploads_dir, upload_id):
		upload_instance = cls(
			uploads_dir, upload_id
		)

		if upload_instance.root_dir.is_dir():
			return upload_instance
		else:
			return None

	@property
	def chunks_dpath(self):
		if self._chunks_dpath != None:
			return self._chunks_dpath

		self._chunks_dpath = self.root_dir / 'chunks'

		self._chunks_dpath.mkdir(exist_ok=True)

		return self._chunks_dpath

	@property
	def info_fpath(self):
		if self._info_fpath != None:
			return self._info_fpath

		self._info_fpath = self.root_dir / 'info.json'

		return self._info_fpath

	@property
	def info_data(self):
		if self._info_data != None:
			return self._info_data

		self._info_data = TDict()

		if self.info_fpath.is_file():
			self._info_data.real_dict = json.loads(
				self.info_fpath.read_bytes()
			)
		else:
			self._info_data.real_dict = {
				'chunk_size':              None,
				'chunk_amount':            None,
				'allocated_tstamp':        unix_now(),
				'last_upload_tstamp':      unix_now(),
				'last_chunk_index':        0,
				'last_chunk_retry_amount': 0,
				'max_chunk_retry_amount':  self.DEFAULT_MAX_RETRIES,
			}

			self.save_info()

		return self._info_data

	@property
	def chunk_size(self):
		if self._chunk_size != None:
			return self._chunk_size

		self._chunk_size = self.info_data['chunk_size']
		self.save_info()

		return self._chunk_size

	@property
	def chunk_amount(self):
		if self._chunk_amount != None:
			return self._chunk_amount

		self._chunk_amount = self.info_data['chunk_amount']
		self.save_info()

		return self._chunk_amount

	@property
	def chunk_array(self):
		if self._chunk_array:
			return self._chunk_array

		self._chunk_array = WaferFileUploadChunkArray(
			self,
			self.chunks_dpath,
			self.chunk_size,
			self.chunk_amount,
		)

		return self._chunk_array

	def save_info(self):
		with self.info_data.edit() as info_data:
			self.info_fpath.write_bytes(
				json.dumps(info_data).encode()
			)











