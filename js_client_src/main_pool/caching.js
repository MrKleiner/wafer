


// an array containing blob urls pointing to preview URLs
$this.preview_cache = []
$this.preview_cache_add = function(imgp=null, imgdata=null)
{
	// don't bother if something broke
	// also, don't add shit twice...
	// todo: use path hashes instead of full paths ?
	if (!imgp || !imgdata || imgp in $this.preview_cache){return}

	// basically, new items are always accepted
	// when the cache is too big - the last item is deleted and a new one is added

	// todo: make 500 an adjustable number
	if ($this.preview_cache.length >= 500){
		// delete fist element from array
		// and also delete shit from browser cache
		// important todo: simply define the URL sys with a const in the top of the core
		obj_url.revokeObjectURL($this.preview_cache[0].imgdata)
		$this.preview_cache.shift()
	}

	// add new requested element
	$this.preview_cache.push({
		'imgp': imgp,
		'imgdata': imgdata
	})
}


// important todo: is it possible to simply check whether an object exists in the given array ?
$this.preview_cache_pull = function(query)
{
	for (var entry of $this.preview_cache){
		if (entry.imgp == query){
			return entry.imgdata
		}
	}
	return null
}


// a small cache of fullres pictures
// currently hardcoded 16
$this.fm_cache = [];
$this.cache_fullres_media = function(url)
{
	if ($this.fm_cache.length > 16){
		obj_url.revokeObjectURL($this.fm_cache[0])
		$this.fm_cache.shift()
	}
	$this.fm_cache.push(url)
}






