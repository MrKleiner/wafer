import sqlite3
import contextlib
import json
import zlib
import base64

from pathlib import Path

from .wafer_util import *


THISDIR = Path(__file__).parent



class BasicDBConnection(NamedPrint):
	PRAGMA = (
		'PRAGMA journal_mode = WAL;',
		'PRAGMA foreign_keys = ON;',
		'PRAGMA synchronous =  NORMAL;',
		'PRAGMA busy_timeout = 6967;',
	)

	def __init__(self, dbpath, reuse=None):
		self.dbpath = dbpath

		self.reuse = reuse

		self._connection = None
		self._begin = None
		self._cursor_obj = None
		self._exec = None
		self._exec_many = None
		self._exec_script = None
		self._commit = None
		self._close = None

		self._fetchone = None
		self._fetchall = None

	@staticmethod
	def _empty(*args, **kwargs):
		pass

	@staticmethod
	def iter_results(cursor, batch_size=420, do_close=True):
		try:
			while (rows := cursor.fetchmany(batch_size)):
				for r in rows:
					yield dict(r)
		finally:
			if do_close:
				cursor.close()

	@contextlib.contextmanager
	def temp_cursor(self):
		cur = self.connection.cursor()
		try:
			yield cur
		finally:
			cur.close()

	@classmethod
	def db_html(cls, db_fpath, tplate_dir, tables):
		result_data = []

		with cls(db_fpath) as dbcon:
			for table_id in tables:
				tdata = {
					'tname': table_id,
					'content': [],
				}

				dbcon.exec(
					f"""PRAGMA table_info({table_id})"""
				)

				tdata['layout'] = [
					i[1] for i in dbcon.fetchall()
				]

				dbcon.exec(
					f"""SELECT * FROM {table_id};"""
				)

				for trow in dbcon.fetchall():
					tdata['content'].append(
						[i[1] for i in dict(trow).items()]
					)

				result_data.append(tdata)

		tplate_dir = Path(tplate_dir)

		html = (
			(tplate_dir / 'base_page.html')
			.read_bytes()
			.replace(
				b'@report_style@',
				(tplate_dir / 'style.css').read_bytes()
			)
		)

		script = (
			(tplate_dir / 'script.js')
			.read_bytes()
			.replace(
				b'@tables@',
				base64.b64encode(
					zlib.compress(
						json.dumps(result_data).encode(),
						level=9
					)
				)
			)
		)

		return html.replace(
			b'@report_script@',
			script
		)

	@property
	def connection(self):
		if self._connection:
			return self._connection

		if self.reuse:
			self._connection = self.reuse.connection
			return self._connection

		self._connection = sqlite3.connect(str(self.dbpath))
		self._connection.row_factory = sqlite3.Row

		for cmd in self.PRAGMA:
			self._connection.execute(cmd)

		return self._connection

	@property
	def cursor_obj(self):
		if self._cursor_obj:
			return self._cursor_obj

		self._cursor_obj = self.connection.cursor()
		return self._cursor_obj

	@property
	def exec(self):
		if self._exec:
			return self._exec

		self._exec = self.cursor_obj.execute
		return self._exec

	@property
	def exec_many(self):
		if self._exec_many:
			return self._exec_many

		self._exec_many = self.cursor_obj.executemany
		return self._exec_many

	@property
	def exec_script(self):
		if self._exec_script:
			return self._exec_script

		self._exec_script = self.cursor_obj.executescript
		return self._exec_script

	@property
	def commit(self):
		if self._commit:
			return self._commit

		if not self._connection:
			return self._empty

		self._commit = self.connection.commit
		return self._commit

	@property
	def close(self):
		if self._close:
			return self._close

		if not self._connection:
			return self._empty

		self._close = self.connection.close
		return self._close

	@property
	def fetchone(self):
		if self._fetchone:
			return self._fetchone

		self._fetchone = self.cursor_obj.fetchone
		return self._fetchone

	@property
	def fetchall(self):
		if self._fetchall:
			return self._fetchall

		self._fetchall = self.cursor_obj.fetchall
		return self._fetchall


	def finish(self, e_type, e_value, e_traceback):
		try:
			if self._connection:
				if e_type is None:
					self._connection.commit()
				else:
					if issubclass(e_type, sqlite3.Error):
						print('SQLITE FATAL:', e_value)

					self._connection.rollback()
		finally:
			if not self.reuse:
				self.close()

			if self.reuse and self._cursor_obj:
				try:
					self._cursor_obj.close()
				except Exception as e:
					print_exception_framed(e)


		return False


	def __enter__(self):
		return self

	def __exit__(self, *args):
		self.finish(*args)



class DBActionsGeneric:
	Q_SELECT_GENERIC = """
		SELECT *
		FROM  %table
		WHERE %col = ?;
	"""

	Q_UPDATE_GENERIC = """
		UPDATE %table
		SET %tgt_col = ?
		WHERE %search_col = ?;
	"""

	Q_DELETE_GENERIC = """
		DELETE FROM %table
		WHERE %search_col = ?;
	"""

	Q_INSERT_GENERIC = """
		INSERT OR IGNORE INTO %table (%COLS)
		VALUES (%VALS);
	"""

	Q_INSERT_RETURNING = """
		INSERT OR IGNORE INTO %table (%COLS)
		VALUES (%VALS)
		RETURNING *;
	"""

	def __init__(self, table, db_con):
		self.table = table
		self.db_con = db_con

	def select_generic_one(self, col_name, col_content):
		self.db_con.exec(
			self.Q_SELECT_GENERIC
			.replace('%table', self.table)
			.replace('%col', col_name),

			(col_content,)
		)

		if (result := self.db_con.fetchone()):
			return dict(result)

		return None

	def select_generic_all(self, col_name, col_content):
		with self.db_con.temp_cursor() as cursor:
			cursor.execute(
				self.Q_SELECT_GENERIC
				.replace('%table', self.table)
				.replace('%col', col_name),

				(col_content,)
			)

			for i in self.db_con.iter_results(cursor):
				yield i

	def update_generic(self, search, update):
		search_col, search_val = search
		upd_col, upd_val = update

		self.db_con.exec(
			self.Q_UPDATE_GENERIC
			.replace('%table', self.table)
			.replace('%tgt_col', upd_col)
			.replace('%search_col', search_col),

			(upd_val, search_val,)
		)

	def delete_generic(self, search_col, search_val):
		self.db_con.exec(
			self.Q_DELETE_GENERIC
			.replace('%table', self.table)
			.replace('%search_col', search_col),

			(search_val,)
		)

	def insert_generic(self, data):
		keys = data.keys()

		self.db_con.exec(
			self.Q_INSERT_GENERIC
			.replace('%table', self.table                      )
			.replace('%COLS',  ','.join(keys)                  )
			.replace('%VALS',  ','.join(f':{i}' for i in keys) ),
			data
		)

	def insert_returning(self, data):
		keys = data.keys()

		return self.db_con.exec(
			self.Q_INSERT_RETURNING
			.replace('%table', self.table)
			.replace('%COLS', ','.join(keys))
			.replace('%VALS', ','.join(f':{i}' for i in keys)),
			data
		).fetchone()



class DBAUploadInstance(NamedPrint):
	SCHEME_FPATH = THISDIR / 'upload_instance.sql'

	Q_COUNT_MAX_RETRIES = """
		SELECT MAX(amount) FROM (
			SELECT COUNT(*) AS amount FROM journal
			GROUP BY chunk_index
		);
	"""

	Q_SEL_ALL_KV = """
		SELECT * FROM kv_params;
	"""

	TYPE_MAP = (
		int,
		str,
		None,
	)

	TYPE_MAP_R = (
		int,
		str,
		lambda _: _,
	)

	def __init__(self, parent_dir, db_con=None):
		self.parent_dir = parent_dir
		self.db_fpath = self.parent_dir / 'upload_info.wafer'

		self.ta_kv_params = None
		self.ta_journal = None

		self.reuse_db_con = db_con
		self.db_con = None

	def __enter__(self):
		self.db_con = self.reuse_db_con or BasicDBConnection(self.db_fpath)

		self.ta_kv_params = DBActionsGeneric(
			'kv_params',
			self.db_con,
		)

		self.ta_journal = DBActionsGeneric(
			'journal',
			self.db_con,
		)

		return self

	def __exit__(self, *args):
		if not self.reuse_db_con:
			self.db_con.finish(*args)

			self.ta_kv_params = None
			self.ta_journal = None
			self.db_con = None
			self.reuse_db_con = None
		else:
			# self.nprint('Committing reused DB data')
			self.db_con.commit()

	def spawn(self):
		if self.db_con:
			self.db_con.exec_script(
				self.SCHEME_FPATH.read_text()
			)
			return

		with BasicDBConnection(self.db_fpath) as dbcon:
			dbcon.exec_script(
				self.SCHEME_FPATH.read_text()
			)

	def apply_params(self, prms):
		for p_k, p_v in prms.items():
			self.ta_kv_params.delete_generic('p_k', p_k)
			self.ta_kv_params.insert_generic({
				'p_k': str(p_k),
				'p_v': str(p_v),
				'p_t': self.TYPE_MAP.index(type(p_v)),
			})

	def list_params(self):
		self.db_con.exec(self.Q_SEL_ALL_KV)
		result = {}

		for pdata in self.db_con.fetchall():
			result[pdata['p_k']] = self.TYPE_MAP_R[pdata['p_t']](pdata['p_v'])

		return result

	def write_journal(self, prms):
		self.ta_journal.insert_generic(prms)

	def count_retries(self):
		self.db_con.exec(self.Q_COUNT_MAX_RETRIES)
		return self.db_con.fetchone()[0]





