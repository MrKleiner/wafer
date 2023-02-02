from pathlib import Path
import json, os, shutil


def tree_copy(src, dest, pattern='*'):
	src = Path(src)
	dest = Path(dest) / src.name
	for tgt in src.rglob(pattern):
		rel = tgt.relative_to(src)
		if tgt.is_dir():
			(dest / rel).mkdir(parents=True, exist_ok=True)
		if tgt.is_file():
			(dest / rel.parent).mkdir(parents=True, exist_ok=True)
			shutil.copy(tgt, dest / rel)

def wipe_folder(fld):
	fld = Path(fld)
	if fld.is_dir():
		shutil.rmtree(fld)
	fld.mkdir()

thisdir = Path(__file__).parent
project = thisdir.parent

conf = json.loads((thisdir / 'release_info.json').read_bytes())

release_dir = Path(conf['dest']) / f"""wafer_{conf['ver']}_linux"""
release_dir_win = Path(conf['dest']) / f"""wafer_{conf['ver']}_win"""

wipe_folder(release_dir)
wipe_folder(release_dir_win)

# create sys folder
release_dir_web = release_dir / 'web'
release_dir_web_win = release_dir_win / 'web'
release_dir_web.mkdir()
release_dir_web_win.mkdir()


# copy js apis
tree_copy(project / 'apis', release_dir_web)
tree_copy(project / 'apis', release_dir_web_win)

# copy assets (images n shit)
tree_copy(project / 'assets', release_dir_web)
tree_copy(project / 'assets', release_dir_web_win)

# copy html panels
tree_copy(project / 'html_panels', release_dir_web)
tree_copy(project / 'html_panels', release_dir_web_win)

# copy compiled js modules
tree_copy(project / 'js_client', release_dir_web)
tree_copy(project / 'js_client', release_dir_web_win)

# copy htbin (python scripts)
tree_copy(project / 'htbin_src', release_dir_web)
tree_copy(project / 'htbin_src', release_dir_web_win)

# copy setup dir
tree_copy(project / 'setup', release_dir_web)
tree_copy(project / 'setup', release_dir_web_win)

# copy wafer sys
tree_copy(project / 'wsys', release_dir)
tree_copy(project / 'wsys', release_dir_win)

# copy setup html to the root with the name "index.html"
shutil.copy(project / 'setup' / 'setup.html', release_dir_web / 'index.html')
shutil.copy(project / 'setup' / 'setup.html', release_dir_web_win / 'index.html')

# windows specific
tree_copy(project / 'bins', release_dir_win)

# __pycache__ cleanup
caches = [pc for pc in release_dir.rglob('*') if pc.is_dir() and pc.name == '__pycache__']
caches.extend([pc for pc in release_dir_win.rglob('*') if pc.is_dir() and pc.name == '__pycache__'])
for pycl in caches:
	if pycl.is_dir():
		shutil.rmtree(pycl)

# copy other files
additional = (
	'css_index.css',
	# 'index.html',
	'wafer_root.wfrt',
	'wafer.evbinds.js',
)
for adt in additional:
	shutil.copy(project / adt, release_dir_web)
	shutil.copy(project / adt, release_dir_web_win)

