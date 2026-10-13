import contextlib
import uuid
import fnmatch

from .wafer_util import *
from .wafer_exceptions import *

from .wafer_dbsys import DBAUserData

from wcmatch import pathlib as wcmatch_pathlib
from pathlib import Path



class WaferUserCredentials(NamedPrint):
	ALLOWED_PROP_ARRAY = (
		'login',
		'pswd',
		'paused',
		'sugmar',
		'created_tstamp',
		'descr',
		'failed_auth_attempts',
	)

	def __init__(self, userid, wafer_acl, data):
		self.userid = userid
		self.wafer_acl = wafer_acl

		self._login = data['login']
		self._pswd =  data['pswd']

		self._paused = data['paused']
		self._sugmar = data['sugmar']

		self._created_tstamp =       data.get('created_tstamp', None)
		self._descr =                data.get('descr', None)
		self._failed_auth_attempts = data.get('failed_auth_attempts', 0)

		self.batching = False

	@property
	def login(self):
		return self._login

	@property
	def pswd(self):
		return self._pswd

	@property
	def paused(self):
		return bool(self._paused)

	@property
	def sugmar(self):
		return bool(self._sugmar)

	@property
	def created_tstamp(self):
		return self._created_tstamp

	@property
	def descr(self):
		return self._descr

	@property
	def failed_auth_attempts(self):
		return self._failed_auth_attempts


	@login.setter
	def login(self, login):
		login = str(login or '').strip()

		if login == self.login:
			return

		if not login:
			raise WaferDisagrees(
				f'This login (>{login}<) appears to be an empty string '
				"""(No, it can't be an empty string)"""
			)

		if len(login) > 500:
			raise WaferDisagrees(
				f'This login (>{login[0:500]}<) appears to be longer than 500 characters '
				"""(No, it can't be this long)"""
			)

		with self.wafer_acl.edit_db() as acl_db:
			if acl_db.ta_profiles.select_generic_one('login', login):
				raise WaferDisagrees(
					f'The new login (>{login}<) already exists '
					"""(No, you can't have duplicate logins)"""
				)

			acl_db.ta_profiles.update_generic(
				('userid', self.userid ),
				('login',  login       ),
			)

			if not self.batching:
				acl_db.db_con.commit()

		self._login = login

	@pswd.setter
	def pswd(self, pswd):
		pswd = str(pswd or '').strip()

		if (len(pswd.encode()) * 8) > 1024:
			raise WaferDisagrees(
				f'This password (>{pswd[0:64]}<) appears to have more than 1024 bits '
				"""(No, it shouldn't be this long)"""
			)

		if (len(pswd.encode()) * 8) < 50:
			raise WaferDisagrees(
				f"""This password (>{pswd}<) is too short """
				"""(No, you're not allowed to suck ass)"""
			)

		with self.wafer_acl.edit_db() as acl_db:
			# if acl_db.ta_profiles.select_generic_one('pswd', pswd):
			# 	raise WaferDisagrees(
			# 		f'The new password (>{pswd}<) already exists '
			# 		"""(No, you can't have duplicate passwords)"""
			# 	)

			# Update password
			acl_db.ta_profiles.update_generic(
				('userid', self.userid),
				('pswd', pswd),
			)

			# Invalidate tokens
			acl_db.ta_tokens.delete_generic(
				'userid', self.userid
			)

			if not self.batching:
				acl_db.db_con.commit()

		self._pswd = pswd

	@descr.setter
	def descr(self, descr):
		descr = str(descr or '').strip()

		if len(descr.encode()) > (1024 * 3):
			raise WaferDisagrees(
				f'The new description (>{descr[0:30]}...<) '
				'is longer than 3KB... (a short fucking novel it is)'
			)

		with self.wafer_acl.edit_db() as acl_db:
			acl_db.ta_profiles.update_generic(
				('userid', self.userid),
				('descr', descr),
			)

			if not self.batching:
				acl_db.db_con.commit()

		self._descr = descr

	@sugmar.setter
	def sugmar(self, sugmar):
		sugmar = bool(sugmar)

		with self.wafer_acl.edit_db() as acl_db:
			acl_db.ta_profiles.update_generic(
				('userid', self.userid ),
				('sugmar', sugmar      ),
			)

			if not self.batching:
				acl_db.db_con.commit()

		self._sugmar = sugmar

	@paused.setter
	def paused(self, paused):
		paused = bool(paused)

		with self.wafer_acl.edit_db() as acl_db:
			acl_db.ta_profiles.update_generic(
				('userid', self.userid ),
				('paused', paused      ),
			)

			if not self.batching:
				acl_db.db_con.commit()

		self._paused = paused

	@failed_auth_attempts.setter
	def failed_auth_attempts(self, amount):
		amount = int(amount)

		with self.wafer_acl.edit_db() as acl_db:
			acl_db.ta_profiles.update_generic(
				('userid',               self.userid ),
				('failed_auth_attempts', amount      ),
			)

			if not self.batching:
				acl_db.db_con.commit()

		self._failed_auth_attempts = amount


	def update(self, data_dict):
		self.batching = True

		try:
			for key, val in (data_dict or {}).items():
				if not (key in self.ALLOWED_PROP_ARRAY):
					continue

				setattr(self, key, val)

			with self.wafer_acl.edit_db() as acl_db:
				acl_db.db_con.commit()
		finally:
			self.batching = False



class WaferMaskInstance(NamedPrint):
	ALLOWED_PROP_ARRAY = (
		'raw_text',

		'perm_view',
		'perm_mkfile',
		'perm_mkdir',

		'syntax',
		'descr',
	)

	def __init__(self, wafer_acl, mask_data):
		self.wafer_acl = wafer_acl

		self._mask_id =     mask_data['mask_id']
		self._raw_text =    mask_data['text_lines']

		self._perm_view =   mask_data['perm_view']
		self._perm_mkfile = mask_data['perm_mkfile']
		self._perm_mkdir =  mask_data['perm_mkdir']

		self._syntax =      mask_data['syntax']

		self._descr =       mask_data['descr']

		self._wcard_array = None

		self.batching = False

	@property
	def wcard_array(self):
		if self._wcard_array != None:
			return self._wcard_array

		self._wcard_array = tuple(
			line.strip() for line
			in self.raw_text.split('\n')

			if line.strip()
			and not line.strip().startswith('#')
		)

		return self._wcard_array


	@property
	def mask_id(self):
		return self._mask_id

	@property
	def raw_text(self):
		return self._raw_text

	@property
	def perm_view(self):
		return self._perm_view

	@property
	def perm_mkfile(self):
		return self._perm_mkfile

	@property
	def perm_mkdir(self):
		return self._perm_mkdir

	@property
	def syntax(self):
		return self._syntax

	@property
	def descr(self):
		return self._descr


	@perm_view.setter
	def perm_view(self, val):
		self._perm_view = int(val)

		with self.wafer_acl.edit_db() as acl_db:
			acl_db.ta_masks.update_generic(
				('mask_id',    self.mask_id    ),
				('perm_view',  self._perm_view ),
			)

			if not self.batching:
				acl_db.db_con.commit()

	@perm_mkfile.setter
	def perm_mkfile(self, val):
		self._perm_mkfile = int(val)

		with self.wafer_acl.edit_db() as acl_db:
			acl_db.ta_masks.update_generic(
				('mask_id',     self.mask_id      ),
				('perm_mkfile', self._perm_mkfile ),
			)

			if not self.batching:
				acl_db.db_con.commit()

	@perm_mkdir.setter
	def perm_mkdir(self, val):
		self._perm_mkdir = int(val)

		with self.wafer_acl.edit_db() as acl_db:
			acl_db.ta_masks.update_generic(
				('mask_id',    self.mask_id     ),
				('perm_mkdir', self._perm_mkdir ),
			)

			if not self.batching:
				acl_db.db_con.commit()


	@raw_text.setter
	def raw_text(self, val):
		self._wcard_array = None
		self._raw_text = str(val or '')

		with self.wafer_acl.edit_db() as acl_db:
			acl_db.ta_masks.update_generic(
				('mask_id',    self.mask_id   ),
				('text_lines', self._raw_text ),
			)

			if not self.batching:
				acl_db.db_con.commit()

	@syntax.setter
	def syntax(self, val):
		self._syntax = int(val or 0)

		with self.wafer_acl.edit_db() as acl_db:
			acl_db.ta_masks.update_generic(
				('mask_id',    self.mask_id ),
				('syntax',     self._syntax ),
			)

			if not self.batching:
				acl_db.db_con.commit()

	@descr.setter
	def descr(self, val):
		self._descr = str(val or '')

		with self.wafer_acl.edit_db() as acl_db:
			acl_db.ta_masks.update_generic(
				('mask_id',    self.mask_id ),
				('descr',      self._descr  ),
			)

			if not self.batching:
				acl_db.db_con.commit()


	def check_path(self, tgt_path):
		if self.syntax == 0:
			tgt_path = wcmatch_pathlib.PurePath(tgt_path)

		if self.syntax == 1:
			tgt_path = str(tgt_path)

		for wcard_str in self.wcard_array:
			if self.syntax == 0:
				if tgt_path.globmatch(
					wcard_str,
					flags=wcmatch_pathlib.GLOBSTAR
				):
					return True

			if self.syntax == 1:
				if fnmatch(tgt_path, wcard_str):
					return True

		return False

	def update(self, data_dict):
		self.batching = True

		try:
			for key, val in (data_dict or {}).items():
				if not (key in self.ALLOWED_PROP_ARRAY):
					continue

				setattr(self, key, val)

			with self.wafer_acl.edit_db() as acl_db:
				acl_db.db_con.commit()
		finally:
			self.batching = False



class WaferUserMasks(NamedPrint):
	def __init__(self, userid, wafer_acl):
		self.userid = userid
		self.wafer_acl = wafer_acl

		self._mask_array = None

	@property
	def mask_array(self):
		if self._mask_array != None:
			return self._mask_array

		with self.wafer_acl.edit_db() as acl_db:
			self._mask_array = acl_db.pull_masks(
				self.userid
			)

		self._mask_array = tuple(
			WaferMaskInstance(self.wafer_acl, m)
			for m in (self._mask_array or ())
		)

		return self._mask_array

	def check_path(self, tgt_path):
		# Everything is prohibited by default
		perm_view =   False
		perm_mkfile = False
		perm_mkdir =  False

		for mask in self.mask_array:
			if mask.check_path(tgt_path):
				# view
				if mask.perm_view == 1:
					perm_view = True
				if mask.perm_view == 2:
					perm_view = False

				# mkfile
				if mask.perm_mkfile == 1:
					perm_mkfile = True
				if mask.perm_mkfile == 2:
					perm_mkfile = False

				# mkdir
				if mask.perm_mkdir == 1:
					perm_mkdir = True
				if mask.perm_mkdir == 2:
					perm_mkdir = False

		return (
			perm_view,
			perm_mkfile,
			perm_mkdir,
		)

	def update(self, mask_id_array):
		self._mask_array = None

		with self.wafer_acl.edit_db() as acl_db:
			self._mask_array = acl_db.apply_masks(
				self.userid,
				mask_id_array,
			)

			acl_db.db_con.commit()



class WaferUserInstance(NamedPrint):
	def __init__(self, wafer_acl, userid):
		if not userid:
			raise WaferDisagrees(
				'FATAL: Invalid userid'
			)

		self.wafer_acl = wafer_acl

		self.userid = userid

		self._creds = None
		self._masks = None

	@property
	def creds(self):
		if self._creds != None:
			return self._creds

		self._creds = False

		with self.wafer_acl.edit_db() as acl_db:
			user_creds = acl_db.ta_profiles.select_generic_one(
				'userid', self.userid
			)

		if user_creds:
			self._creds = WaferUserCredentials(
				self.userid, self.wafer_acl, user_creds
			)

		return self._creds

	@property
	def masks(self):
		if self._masks:
			return self._masks

		self._masks = WaferUserMasks(self.userid, self.wafer_acl)

		return self._masks

	def apply_masks(self, mask_id_array):
		self._masks = None

		with self.wafer_acl.edit_db() as acl_db:
			acl_db.ta_mask_linkage.delete_generic(
				'userid', self.userid
			)

			for idx, mask_id in enumerate(mask_id_array):
				acl_db.ta_mask_linkage.insert_generic({
					'mask_id': mask_id,
					'userid':  self.userid,
					'idx':     idx,
				})

			acl_db.db_con.commit()



class WaferACL(NamedPrint):
	def __init__(self, db_fpath, clocked_db=None):
		self.db_fpath = db_fpath
		self.clocked_db = clocked_db

	@contextlib.contextmanager
	def edit_db(self):
		if self.clocked_db:
			with self.clocked_db.con(self.db_fpath) as dbcon:
				with DBAUserData(self.db_fpath.parent, dbcon) as dba:
					yield dba
		else:
			with DBAUserData(self.db_fpath.parent) as dba:
				yield dba

	def pull_user(self, userid=None, login=None):
		return WaferUserInstance(
			self,
			userid,
		)

	def auth_user(self, login, pswd):
		with self.edit_db() as acl_db:
			user_data = acl_db.ta_profiles.select_generic_one(
				'login', login
			)

		if not user_data:
			return (False, None)

		wafer_user = WaferUserInstance(
			self,
			user_data['userid'],
		)

		if wafer_user.creds.pswd != pswd:
			wafer_user.creds.failed_auth_attempts += 1
			return (False, wafer_user)

		wafer_user.creds.failed_auth_attempts = 0

		return (True, wafer_user)

	def create_user(self, login, pswd):
		userid = str(uuid.uuid4())

		try:
			with self.edit_db() as acl_db:
				acl_db.ta_profiles.insert_generic({
					'userid': userid,
					'login': str(uuid.uuid4()),
					'pswd':  str(uuid.uuid4()),
					'created_tstamp': unix_now(),
				})

				acl_db.db_con.commit()

			user_data = WaferUserInstance(
				self,
				userid,
			)

			user_data.creds.update({
				'login': login,
				'pswd': pswd,
			})

			return user_data
		except Exception as e:
			print_exception_framed(e)

			with self.edit_db() as acl_db:
				acl_db.ta_profiles.delete_generic(
					'userid', userid
				)

				acl_db.db_con.commit()

			raise e

	def alloc_masks(self, amount=1):
		mask_array = []
		with self.edit_db() as acl_db:
			for _ in range(amount):
				mask_array.append(
					WaferMaskInstance(
						self,
						acl_db.ta_masks.insert_returning(),
					)
				)

			acl_db.db_con.commit()

		return mask_array





