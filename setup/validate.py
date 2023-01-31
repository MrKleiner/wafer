from pathlib import Path
import json, cgi, cgitb, sys, os, socket
import subprocess as sp

cgitb.enable()

def is_port_in_use(port):
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		return s.connect_ex(('localhost', port)) == 0


def validate_ftp_root(tgt_path):
	tgt_path = Path(tgt_path)
	if not tgt_path.is_dir() or tgt_path == Path('.'):
		return 'This directory does not exist'
	else:
		return True


def validate_ffmpeg(tgt_path):
	tgt_path = Path(tgt_path)
	if not tgt_path.is_file():
		return 'The specified file does not exist'
	try:
		ffmpeg_prms = [
			str(tgt_path),
			'-version'
		]

		mpeg = None
		with sp.Popen(ffmpeg_prms, stdout=sp.PIPE, bufsize=10**8) as mpeg_pipe:
			mpeg = mpeg_pipe.stdout.read()

		# if mpeg == None or not b'version' in mpeg.lower() or not b'ffmpeg' in mpeg.lower():
		if not b'ffmpeg version' in mpeg.lower():
			return 'The specified file does not look like ffmpeg'
	except Exception as e:
		return 'The specified file does not look like ffmpeg'

	return True


def validate_ffprobe(tgt_path):
	tgt_path = Path(tgt_path)
	if not tgt_path.is_file():
		return 'The specified file does not exist'
	try:
		ffprobe_prms = [
			str(tgt_path),
			'-version'
		]

		probe = b''
		with sp.Popen(ffprobe_prms, stdout=sp.PIPE, bufsize=10**8) as probe_pipe:
			probe = probe_pipe.stdout.read()

		if not b'version' in probe.lower() or not b'ffprobe' in probe.lower():
			return 'The specified file does not look like ffprobe'
	except Exception as e:
		return 'The specified file does not look like ffprobe'


	return True


def validate_magix(tgt_path):
	tgt_path = Path(tgt_path)
	if not tgt_path.is_file():
		return 'The specified file does not exist'
	try:
		magix_prms = [
			str(tgt_path),
			'-version'
		]

		magix = b''
		with sp.Popen(magix_prms, stdout=sp.PIPE, bufsize=10**8) as magix_pipe:
			magix = magix_pipe.stdout.read()

		if not b'version' in magix.lower() or not b'magick' in magix.lower():
			return 'The specified file does not look like ImageMagick'
	except Exception as e:
		return 'The specified file does not look like ImageMagick'


	return True

def validate_auth_db(tgt_path):
	tgt_path = Path(tgt_path)
	if not tgt_path.parent.is_dir() or tgt_path.parent == Path('.'):
		return 'The parent dir of the specified dir does not exist'
	else:
		return True

def validate_sys_db(tgt_path):
	tgt_path = Path(tgt_path)
	if not tgt_path.parent.is_dir() or tgt_path.parent == Path('.'):
		return 'The parent dir of the specified dir does not exist'
	else:
		return True

def validate_watchdog_port(prt):
	return not is_port_in_use(int(prt))

def validate_upl_sys_port(prt):
	return not is_port_in_use(int(prt))

def validate(inf):
	
	vdict = {
		'ftp_root': validate_ftp_root,
		'ffmpeg_path': validate_ffmpeg,
		'ffprobe_path': validate_ffprobe,
		'magix_path': validate_magix,
		'authdb_path': validate_auth_db,
		'sysdb_path': validate_sys_db,
		'watchdog_port': validate_watchdog_port,
		'upload_service_port': validate_upl_sys_port,
	}

	validated = {}
	has_err = False
	for v in inf:
		if v in vdict:
			validated[v] = vdict[v](inf[v])
			if validated[v] == False:
				has_err = True

	return [(len(validated) == len(vdict)) and not has_err, validated]









if __name__ == '__main__':
	incoming_info = json.loads(sys.stdin.buffer.read())

	print('Content-Type: application/octet-stream\r\n\r\n')
	print(json.dumps(validate(incoming_info)))

