


video = [
	'mp4',
	# IMPORTANT: RECHECK
	'mov',
	'webm',
	'ts',
	'mts',
	'mkv',
	'avi',
	'mpeg',
	'ogv',
	'3gp',
	# todo: but like... really ?????
	'wmv',
	'flv',
]

# image formats supported by the combination of ffmpeg and image magick
img_total = [
	'jpg',
	'jpeg',
	'jp2',
	'j2k',
	'png',
	'tif',
	'tiff',
	'tga',
	'webp',
	'psd',
	'apng',
	'gif',
	'avif',
	'bmp',
	'dib',
	'raw',
	'arw',
	'jfif',
	'jif',
	'hdr',
	'exr',
	'dds',
	'ico',
	'pfm',
	'svg',
]

# special means ffmpeg cannot deal with it
# but image magick can
# the reason ffmpeg is a preferred option is because it works twice as fast compared to imagemagick
img_magick = [
	'tga',
	'psd',
	'arw',
	'raw',
	'hdr',
	# todo: ffmpeg can actually deal with exr files...
	'exr',
	'dds',
	'ico',
	'pfm',
	'svg',
]




