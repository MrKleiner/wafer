
# jsrc can either be a json string, an object OR path to the json file
def compile_json(jsrc, jdest, as_path=False):
	import json, py_compile
	from pathlib import Path

	if as_path == True:
		jsrc = json.loads(Path(jsrc).read_bytes())
	else:
		# if type(jsrc) == str:
		jsrc = json.loads(jsrc)
	jbuffer = 'null = None' + '\n'
	jbuffer += 'false = False' + '\n'
	jbuffer += 'true = True' + '\n'
	jbuffer += 'data = '
	jbuffer += json.dumps(jsrc, indent='\t')

	tmp = Path(jdest.with_suffix('.py'))
	tmp.write_text(jbuffer)

	py_compile.compile(str(tmp), cfile=tmp.with_suffix('.pyc').name)

	tmp.unlink()

