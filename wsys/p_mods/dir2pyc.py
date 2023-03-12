

def dir2pyc(inpdir, outdir, wipe=True, exclude=[]):
	import py_compile, shutil
	from pathlib import Path

	inpdir = Path(inpdir)
	outdir = Path(outdir)

	if wipe and outdir.is_dir():
		shutil.rmtree(outdir)
	outdir.mkdir(exist_ok=True)

	for pyfile in inpdir.rglob('*.py'):
		if pyfile.name in exclude:
			continue

		src_file = pyfile.relative_to(inpdir)

		tgt_dest = outdir / src_file

		if not tgt_dest.parent.is_dir():
			tgt_dest.parent.mkdir(parents=True, exist_ok=True)

		py_compile.compile(str(tgt_dest), cfile=pyfile.with_suffix('.pyc').name)


