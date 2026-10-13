import datetime
import os
import sys
import contextlib
import time

from .jag.jag_util import (
	print_exception_framed,
	NamedPrint,
	TDict,
)

try:
	import msvcrt
except ImportError:
	msvcrt = None

try:
	import fcntl
except ImportError:
	fcntl = None



def unix_now():
	return int(
		datetime.datetime.now().timestamp()
	)



@contextlib.contextmanager
def file_lock(path, timeout=None):
	lock_file = open(path, 'a+b')
	acquired = False
	deadline = None if (timeout is None) else (time.monotonic() + timeout)

	try:
		if sys.platform == 'win32':
			lock_file.seek(0, os.SEEK_END)

			if lock_file.tell() == 0:
				lock_file.write(b'\0')
				lock_file.flush()

		while True:
			try:
				if sys.platform == 'win32':
					lock_file.seek(0)
					msvcrt.locking(
						lock_file.fileno(),
						msvcrt.LK_NBLCK,
						1
					)
				else:
					fcntl.flock(
						lock_file.fileno(),
						fcntl.LOCK_EX | fcntl.LOCK_NB
					)

				acquired = True
				break

			except OSError:
				if deadline is not None and time.monotonic() >= deadline:
					raise TimeoutError(
						f'Could not acquire lock: {path}'
					)

				time.sleep(
					0.05 if deadline is None
					else min(0.05, max(0, deadline - time.monotonic()))
				)

		yield

	finally:
		try:
			if acquired:
				if sys.platform == 'win32':
					lock_file.seek(0)
					msvcrt.locking(
						lock_file.fileno(),
						msvcrt.LK_UNLCK,
						1
					)
				else:
					fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
		finally:
			lock_file.close()


