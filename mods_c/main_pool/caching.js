
if (!window.bootlegger){window.bootlegger = {}};

if (!window.bootlegger.main_pool){window.bootlegger.main_pool={}};



// an array containing blob urls pointing to preview URLs
window.bootlegger.main_pool.preview_cache = []
window.bootlegger.main_pool.preview_cache_add = function(imgp=null, imgdata=null)
{
	// don't bother if something broke
	// also, don't add shit twice...
	// todo: use path hashes instead of full paths ?
	if (!imgp || !imgdata || imgp in window.bootlegger.main_pool.preview_cache){return}

	// basically, new items are always accepted
	// when the cache is too big - the last item is deleted and a new one is added

	// todo: make 500 an adjustable number
	if (window.bootlegger.main_pool.preview_cache.length >= 500){
		// delete fist element from array
		// and also delete shit from browser cache
		// important todo: simply define the URL sys with a const in the top of the core
		obj_url.revokeObjectURL(window.bootlegger.main_pool.preview_cache[0].imgdata)
		window.bootlegger.main_pool.preview_cache.shift()
	}

	// add new requested element
	window.bootlegger.main_pool.preview_cache.push({
		'imgp': imgp,
		'imgdata': imgdata
	})
}


// important todo: is it possible to simply check whether an object exists in the given array ?
window.bootlegger.main_pool.preview_cache_pull = function(query)
{
	for (var entry of window.bootlegger.main_pool.preview_cache){
		if (entry.imgp == query){
			return entry.imgdata
		}
	}
	return null
}


// a small cache of fullres pictures
// currently hardcoded 16
window.bootlegger.main_pool.fm_cache = [];
window.bootlegger.main_pool.cache_fullres_media = function(url)
{
	if (window.bootlegger.main_pool.fm_cache.length > 16){
		obj_url.revokeObjectURL(window.bootlegger.main_pool.fm_cache[0])
		window.bootlegger.main_pool.fm_cache.shift()
	}
	window.bootlegger.main_pool.fm_cache.push(url)
}






