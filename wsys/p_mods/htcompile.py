

def compile_server(srv):
	import py_compile, shutil
	from pathlib import Path

	server_dir = Path(srv)

	if (server_dir / 'htbin').is_dir():
		shutil.rmtree(server_dir / 'htbin')
	(server_dir / 'htbin').mkdir(exist_ok=True)

	for pyfile in (server_dir / 'htbin_src').rglob('*.py'):
		src_file = pyfile.relative_to(server_dir / 'htbin')

		tgt_dest = server_dir / 'htbin' / src_file

		if not tgt_dest.parent.is_dir():
			tgt_dest.parent.mkdir(parents=True, exist_ok=True)

		# if not pyfile.name in ('server_config.py', 'server_setup.py', 'factory_reset.py'):
			# compile the file
		py_compile.compile(str(tgt_dest), cfile=pyfile.name.with_suffix('.pyc'))