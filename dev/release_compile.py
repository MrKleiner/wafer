from pathlib import Path
import json, os, shutil
os.system('cls')
print('Compiling.')


# copy tree/file to win/linux/both
def duplicate(dirsrc, destlin, destwin=None, tolinux=True, towin=True, pattern='*', _ignore=[]):
	if not destwin:
		destwin = destlin

	dirsrc = Path(dirsrc)
	destlin = Path(destlin)
	destwin = Path(destwin)

	if dirsrc.is_dir():
		if tolinux:
			tree_copy(dirsrc, destlin, pattern, ignore=_ignore)
		if towin:
			tree_copy(dirsrc, destwin, pattern, ignore=_ignore)

		return

	if dirsrc.is_file():
		if tolinux:
			shutil.copy(dirsrc, destlin)
		if towin:
			shutil.copy(dirsrc, destwin)

# Write data to a file to win/linux
def write_file(content, destlin, destwin=None, tolinux=True, towin=True):
	if not destwin:
		destwin = destlin
	destlin = Path(destlin)
	destwin = Path(destwin)

	if tolinux:
		destlin.write_text(content)
	if towin:
		destwin.write_text(content)


def dict_replace(src, matches):
	for drp in matches:
		src = src.replace(drp, matches[drp])
	return src


# Copy a tree of files to a new location
def tree_copy(src, dest, pattern='*', ignore=[]):
	src = Path(src)
	dest = Path(dest) / src.name
	for tgt in src.rglob(pattern):
		if tgt.name in ignore:
			continue
		rel = tgt.relative_to(src)
		if tgt.is_dir():
			(dest / rel).mkdir(parents=True, exist_ok=True)
		if tgt.is_file():
			(dest / rel.parent).mkdir(parents=True, exist_ok=True)
			shutil.copy(tgt, dest / rel)

# Delete a dir tree and then recreate root
def wipe_folder(fld):
	fld = Path(fld)
	if fld.is_dir():
		shutil.rmtree(fld)
	fld.mkdir()



# the "dev" dir
thisdir = Path(__file__).parent
# Root where all the source files lay
project = thisdir.parent

# Compilation config
conf = json.loads((thisdir / 'release_info.json').read_bytes())

# Put Linux release in this dir
release_dir = Path(conf['dest']) / f"""wafer_{conf['ver']}_linux"""
# Put Windows release in this dir
release_dir_win = Path(conf['dest']) / f"""wafer_{conf['ver']}_win"""

# Make sure that the release destination dirs are empty
wipe_folder(release_dir)
wipe_folder(release_dir_win)

# create JS client dir
release_dir_web = release_dir / 'web'
release_dir_web_win = release_dir_win / 'web'
release_dir_web.mkdir()
release_dir_web_win.mkdir()


_common_dirs = (
	'apis',
	'assets',
	'html_panels',
	'js_client',
	'wsys',
	'setup',
)
for dtree in _common_dirs:
	duplicate(project / _common_dirs, release_dir_web, release_dir_web_win)

# copy htbin (python scripts)
duplicate(project / 'htbin_src', release_dir_web, release_dir_web_win, _ignore=('jag.py',))


# copy wafer_util from wsys to htbin_src
duplicate(
	project / 'wsys' / 'p_mods' / 'wafer_util.py',
	release_dir_web     / 'htbin_src',
	release_dir_web_win / 'htbin_src'
)

# copy lstruct shit
lstruct = Path(conf['lstruct']).read_text().split('# @\n# Rubbish split\n# @')[0].strip()
write_file(
	lstruct,
	release_dir     / 'wsys' / 'p_mods' / 'lightstruct.py',
	release_dir_win / 'wsys' / 'p_mods' / 'lightstruct.py',
)



# copy setup html to the root with the name "index.html"
duplicate(
	project / 'setup' / 'setup.html',
	release_dir_web     / 'index.html',
	release_dir_web_win / 'index.html'
)

# windows specific binaries like imagemagick n shit
duplicate(project / 'bins', release_dir_win, tolinux=False)

# __pycache__ cleanup
caches = [pc for pc in release_dir.rglob('*') if pc.is_dir() and pc.name == '__pycache__']
caches.extend([pc for pc in release_dir_win.rglob('*') if pc.is_dir() and pc.name == '__pycache__'])
for pycl in caches:
	if pycl.is_dir():
		shutil.rmtree(pycl)

# copy some files to the JS client release dir
additional = (
	'css_index.css',
	# 'index.html',
	'wafer_root.wfrt',
	'wafer.evbinds.js',
)
for adt in additional:
	duplicate(project / adt, release_dir_web, release_dir_web_win)

# Burn version into the files
burn_ver = (
	'htbin_src/server.py',
	'js_client/core/core_base.js',
)
for bv in burn_ver:
	for _platform in (release_dir_web, release_dir_web_win,):
		_tgt = _platform / bv
		_read = _tgt.read_text().replace('$WAFER_VERSION_NUMBER$', conf['ver'])
		_tgt.write_text(_read)





# construct server gateway
jag_burns = {
	'$JAG_FATAL_ERR_MSG$':                'wafer-fatal-error',
	'$JAG_REGULAR_ERR_MSG$':              'wafer-error',
	'$JAG_JATEWAY_ACTION_NOT_FOUND_MSG$': 'raw_exception',
	# important todo: this has to be configurable
	'$JAG_X_FILES_HNAME$':                'X-Sendfile',
}
server_entry = (
	dict_replace(Path(conf['jag']).read_text().strip(), jag_burns),
	(project / 'wsys' / 'p_mods' / 'rd_journal_ctrl.py').read_text().strip(),
	(project / 'htbin_src' / 'server.py').read_text().strip(),
)
write_file(
	'\n\n'.join(server_entry),
	release_dir_web     / 'htbin_src' / 'server.py',
	release_dir_web_win / 'htbin_src' / 'server.py'
)


print('Done.')