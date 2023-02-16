from pathlib import Path
import json, cgi, cgitb, sys, os, socket
import subprocess as sp

cgitb.enable()


def is_port_in_use(port):
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		return s.connect_ex(('localhost', port)) == 0

def validate_path(p):
	tgt_path = Path(p)
	if not tgt_path.is_dir() or tgt_path == Path('.'):
		return False
	else:
		return True

def validate_output(tgt_path, cmd, search):
	tgt_path = Path(tgt_path)
	if not tgt_path.is_file():
		return 'The specified file does not exist'
	try:
		exec_prms = [
			str(tgt_path),
			cmd
		]

		exec_echo = None
		with sp.Popen(exec_prms, stdout=sp.PIPE, bufsize=10**8) as exec_pipe:
			exec_echo = exec_pipe.stdout.read()

		# if mpeg == None or not b'version' in mpeg.lower() or not b'ffmpeg' in mpeg.lower():
		if not search.encode() in exec_echo.lower():
			return False
	except Exception as e:
		return False

	return True









def validate(inf):
	"""
	vdict = {
		'ftp_root': validate_path,
		'ffmpeg_path': validate_output,
		'ffprobe_path': validate_output,
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
	"""




	port_validation = (
		'watchdog_port',
		'upload_service_port',
	)

	echo_validation = (
		('ffmpeg_path', '-version', 'ffmpeg version', """This doesn't look like ffmpeg"""),
		('ffprobe_path', '-version', 'ffprobe version', """This doesn't look like ffprobe"""),
		('magix_path', '-version', 'version: imagemagick', """This doesn't look like Image Magick"""),
	)

	path_validation = (
		'ftp_root',
		'authdb_path',
		'sysdb_path',
	)

	validated = {}
	has_err = False

	# port validation
	for p_vl in port_validation:
		if inf.get(p_vl):
			decision = not is_port_in_use(int(inf[p_vl]))
			# validated[p_vl] = decision
			if decision:
				validated[p_vl] = True
			else:
				validated[p_vl] = 'This port is occupied already'
				has_err = True

	# echo validation
	for e_vl in echo_validation:
		if inf.get(e_vl[0]):
			decision = validate_output(inf[e_vl], e_vl[1], e_vl[2])
			if decision:
				validated[e_vl] = True
			else:
				validated[e_vl] = e_vl[3]
				has_err = True

	# path validation
	for pa_vl in path_validation:
		if inf.get(pa_vl):
			decision = validate_path(inf[pa_vl])
			if decision:
				validated[pa_vl] = True
			else:
				validated[pa_vl] = 'This path is invalid'
				has_err = True


	return [has_err, validated]









if __name__ == '__main__':
	incoming_info = json.loads(sys.stdin.buffer.read())

	print('Content-Type: application/octet-stream\r\n\r\n')
	print(json.dumps(validate(incoming_info)))

