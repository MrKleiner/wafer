


def compile_server():
	import py_compile, shutil
	from pathlib import Path

	thisdir = Path(__file__).absolute().parents[1]

	if (thisdir / 'htbin_c').is_dir():
		shutil.rmtree(str(thisdir / 'htbin_c'))
	(thisdir / 'htbin_c').mkdir(exist_ok=True)

	for pyfile in (thisdir / 'htbin').rglob('*.py'):
		src_file = pyfile.relative_to(thisdir / 'htbin')

		tgt_dest = thisdir / 'htbin_c' / src_file

		if not tgt_dest.parent.is_dir():
			tgt_dest.parent.mkdir(parents=True)

		# copy the original file
		shutil.copy(str(pyfile), str(tgt_dest))

		if not pyfile.name in ('server_config.py', 'server_setup.py', 'factory_reset.py'):
			# compile the file
			compiled = py_compile.compile(str(tgt_dest))
			# move the compiled file to its original place
			shutil.move(compiled, str(tgt_dest.with_name(pyfile.name).with_suffix('.pyc')))
			# remove the compile src
			tgt_dest.unlink()
			# remove the pycache folder
			(tgt_dest.parent / '__pycache__').rmdir()


if __name__ == '__main__':
	compile_server()