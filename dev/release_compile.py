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



# copy js apis
tree_copy(project / 'apis', release_dir)
tree_copy(project / 'apis', release_dir_win)

# copy assets (images n shit)
tree_copy(project / 'assets', release_dir)
tree_copy(project / 'assets', release_dir_win)

# copy html panels
tree_copy(project / 'panels', release_dir)
tree_copy(project / 'panels', release_dir_win)

# copy compiled js modules
tree_copy(project / 'mods_c', release_dir)
tree_copy(project / 'mods_c', release_dir_win)

# copy htbin (python scripts)
tree_copy(project / 'htbin', release_dir)
tree_copy(project / 'htbin', release_dir_win)

# copy setup dir
tree_copy(project / 'setup', release_dir)
tree_copy(project / 'setup', release_dir_win)

# windows specific
tree_copy(project / 'bins', release_dir_win)

# copy other files
additional = (
	'css_index.css',
	'index.html',
	'wafer_root.wfrt',
	'wafer.evbinds.js',
)
for adt in additional:
	shutil.copy(project / adt, release_dir)
	shutil.copy(project / adt, release_dir_win)