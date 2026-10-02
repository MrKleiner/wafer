import datetime

from .jag.jag_util import (
	print_exception_framed,
	NamedPrint,
	TDict,
)




def unix_now():
	return int(
		datetime.datetime.now().timestamp()
	)




