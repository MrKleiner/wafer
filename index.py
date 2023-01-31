# Todo: this is still not an ideal way of structuring this script
from pathlib import Path
server_root = Path(__file__).parent


# important todo: this is still not an ideal check of whether the install script was run or not
# The install script should simply replace this script with index.html
sys.stdout.buffer.write('Content-Type: text/html; charset=utf-8\r\n\r\n'.encode())
if not '.set' in __file__[-16:]:
	import sys
	sys.stdout.buffer.write((server_root / 'setup' / 'setup.html').read_bytes())
else:
	sys.stdout.buffer.write((server_root / 'panels' / 'main.html').read_bytes())






