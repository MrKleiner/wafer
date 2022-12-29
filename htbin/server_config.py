

# Server hosters are probably used to retarded syntaxes by now,
# so this should be fine
# Afterall, this is ~97 times more readable than apache or lighttpd syntax...


# Don't forget that the user running this software should have read/write rights
# for specified folders AND the server root (entire hierarchy starting 1 folder up from htbin) (when running on Linux)

# it's highly recommended to always use forward slashes in the filepaths,
# even when configuring for windows
# (windows support coming soon)

# bro tip: When creating shit from root - don't forget to change the access rights

server_config = {

	# -------------------------------
	#  !!!!!!! Server type !!!!!!!
	# -------------------------------
	# which system are you running (apache, lighttpd...)
	# This is very important and messing this up will break half the system
	# applicable entries are:
	#	lighttpd (this is the only option for now. BUT nothing is hardcoded, so it's just one tiny little thing that has to be tackled)

	# make sure to configure server so that all the .py files inside htbin are executed with python

	"target_sys": "lighttpd",

	# don't touch this
	"xs_override": "",



	# Root of the target file system
	# basically think of this as of FTP root
	"system_root": "/home/basket/wafer_ftp",

	# absolute path to ffmpeg
	# on linux it's usually /usr/bin/ffmpeg /usr/bin/ffprobe
	"ffmpeg": "/usr/bin/ffmpeg",

	# absolute path to ffprobe
	"ffprobe": "/usr/bin/ffprobe",

	# Image Magick executable location
	# On Linux it's pretty weird: /usr/bin/convert
	"magix": "/usr/bin/convert",

	# path to a folder where to unfold the LIGHTWEIGHT database system
	# the folder doesn't has to exist beforehand
	# this databse stores user info, auth system and software config
	# it should never take more than 1-2GB of diskspace
	# ( please place me on an SSD or a really fast HDD :3 )
	"authdb": "/home/basket/wafer_user_db",


	# A database of temp files and media previews
	# the folder doesn't has to exist beforehand
	# it might get quite big
	# aka if serverside zipping is enabled and someone downloads a folder of photos - 
	# ~1GB zip file is generated
	# in addition, all the previews are stored here
	# A switch between serverside and clientside zipping is coming soon
	"sysdb": "/home/basket/wafer_sys_db"
}