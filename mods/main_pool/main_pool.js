
$this.dirlisting = []


$this.set_flist_view_type = function(tp='list')
{
	if (tp == 'list'){
		document.querySelector('mpool').removeAttribute('grid');
		document.querySelector('mpool').setAttribute('list', true);
	}
	if (tp == 'grid'){
		document.querySelector('mpool').removeAttribute('list');
		document.querySelector('mpool').setAttribute('grid', true);
	}
}



$this.module_loader = async function()
{
	print('start loading mpool')
	await $all.core.sysloader('main_pool', true);
	await $this.load_root_dir(false)
	await $this.go_dir_path()
}

$this.go_dir_path = async function()
{
	print('go dir path')
	const urlParams = new URLSearchParams(window.location.search);
	const load_loc = urlParams.get('f');
	const paths = load_loc.trim().strip('/').split('/')

	paths[1] ? (await $this.list_league_matches(paths[1])) : null
	print('godir 1')
	paths[2] ? (await $this.list_match_struct(paths[2])) : null
	print('godir 2')
	paths[3] ? (await $this.list_media(paths[3])) : null
}




$this.load_root_dir = async function(doup=true)
{
	print('mpool load root dir')
	$this.media_units_iteration.kill()
	// list root shite
	const roots = await $all.core.py_get(
		'poolsys/poolsys',
		{
			'action': 'list_leagues'
		},
		'json'
	)
	print('mpool loaded root dir')

	print('fuck this shit', roots)
	doup ? $this.update_vis_path() : null
	// $this.update_vis_path()

	$('mpool flist').empty();
	$this.set_flist_view_type('list');
	// spawn shite
	for (var entry of roots){
		$('mpool flist').append(`
			<flist-entry class="folder league" fldname="${entry}">
				<etype folder>
				</etype>
				<ename>${entry}</ename>
			</flist-entry>
		`)
	}
}


$this.list_league_matches = async function(elm='')
{
	$this.media_units_iteration.kill()
	print('mpool list matches')
	const fld_name = elm.getAttribute ? elm.getAttribute('fldname') : elm;

	window.league = fld_name;
	$this.update_vis_path()


	const full_root = (await $all.core.load_dbfile('root.json', 'json'))['root_path']

	const subroot_flds = await $all.core.py_get(
		'poolsys/poolsys',
		{
			'action': 'list_league_matches',
			'league_name': fld_name
		},
		'json'
	)

	$('mpool flist').empty();
	$this.set_flist_view_type('list');

	// spawn shite
	for (var entry of subroot_flds){
		$('mpool flist').append(`
			<flist-entry class="folder match" fldpath="${entry}">
				<etype folder>
				</etype>
				<ename>${entry}</ename>
			</flist-entry>
		`)
	}
	// now prepend go up
	$('mpool flist').prepend(`
		<flist-entry class="folder" onclick="window.league = null; $this.load_root_dir()">
			<etype folder>
			</etype>
			<ename>../</ename>
		</flist-entry>
	`)

}


$this.list_match_struct = async function(elm='')
{
	print('mpool list match struct')
	// important todo: as was mentioned below this should be a system
	// and not just some random shit
	// update: this is SOME sort of system, but still not what we need
	$this.media_units_iteration.kill()
	$this.dirlisting = [];
	const fld_name = elm.getAttribute ? elm.getAttribute('fldpath') : elm;

	window.league_match = fld_name;
	$this.update_vis_path()

	const dirlisting = await $all.core.py_get(
		'poolsys/poolsys',
		{
			'action': 'list_match_struct',
			'match_name': `${window.league}/${window.league_match}`
		},
		'json'
	)

	print('listed match:', dirlisting)

	$('mpool flist').empty();
	$this.set_flist_view_type('list');

	for (var lst of dirlisting){
		$('mpool flist').append(`
			<flist-entry class="folder struct_entry" fldpath="${lst}">
				<etype folder>
				</etype>
				<ename>${lst}</ename>
			</flist-entry>
		`)
	}

	// now prepend go up
	$('mpool flist').prepend(`
		<flist-entry fldname="${window.league}" class="folder" onclick="window.league_match = null; $this.list_league_matches(this)">
			<etype folder>
			</etype>
			<ename>../</ename>
		</flist-entry>
	`)
}









$this.video_bins = {}
// important todo: it looks like if an element with image url exists - it's being precached
// what are the limits of this ?
// how many elements at once can be precached ?
$this.vidframes_cache = []
$this.spawn_video_unit = async function(vpath)
{
	return new Promise(async function(resolve, reject){

		const fname = vpath.split('/').at(-1).trim()
		const unit_id = lizard.rndwave(32, 'def')

		const video_entry = $(`
			<flist-entry unit_id="${unit_id}" class="media_entry lfs_entry" flpath="${vpath}" flname="${fname}">
				<etype style="background-image: url(./assets/spinning_circle.svg)" vid>
				</etype>
				<ename>${fname}</ename>
			</flist-entry>
		`)
		$('mpool flist').append(video_entry)

		var video_preview = $this.preview_cache_pull(vpath)

		if (!video_preview){
			var video_preview = await $all.core.py_get(
				'poolsys/poolsys',
				{
					'action': 'load_video_preview',
					'video_path': vpath
				},
				'buffer'
			)
			$this.preview_cache_add(vpath, video_preview)
		}

		
		const preview_bin = new window.gigabin(video_preview)
		$this.video_bins[unit_id] = []
		for (var frame of range(100)){
			const imgu = preview_bin.read_file(`frn${frame+1}`, 'obj_url')
			$this.video_bins[unit_id].push(imgu)
			$this.vidframes_cache.push(await $this.await_img_load(imgu))
		}
		video_entry.find('etype')[0].style.backgroundImage = `url(${$this.video_bins[unit_id][0]})`
		resolve(true)

	});
}

$this.flush_preview_frames = function()
{
	for (var rv in $this.video_bins){
		for (var fr of $this.video_bins[rv]){
			(window.URL || window.webkitURL).revokeObjectURL(fr)
		}
	}
	for (var rv of $this.vidframes_cache){
		(window.URL || window.webkitURL).revokeObjectURL(rv)
	}
}

// todo: collapse another multiplier
$this.vidscroll = function(evt, etgt)
{
	// Get bbox relative to viewport
	const pr_id = etgt.closest('flist-entry').getAttribute('unit_id')
	const rect = etgt.getBoundingClientRect()
	// Mouse position relative to element
	const current_x = Math.abs(evt.clientX - rect.left);
	// current / total = current percent progress
	const scroll = int(100 * (current_x / rect.width))
	etgt.style.backgroundImage = `url(${$this.video_bins[pr_id][scroll]})`
}


$this.spawn_image_unit = async function(imgpath)
{
	return new Promise(async function(resolve, reject){
		// todo: the split solution is just rubbish
		const fname = imgpath.split('/').at(-1).trim()
		const media_entry = $(`
			<flist-entry class="media_entry" flpath="${imgpath}" flname="${fname}">
				<etype style="background-image: url(./assets/spinning_circle.svg)" img>
				</etype>
				<ename>${fname}</ename>
			</flist-entry>
		`)

		$('mpool flist').append(media_entry)

		// try pulling shit from cache
		var img_preview = $this.preview_cache_pull(imgpath)

		// else - load from server
		if (!img_preview){
			var img_preview = await $all.core.py_get(
				'poolsys/poolsys',
				{
					'action': 'load_image_preview',
					'image_path': imgpath
				},
				'blob_url'
			)
			$this.preview_cache_add(imgpath, img_preview)
		}

		print(img_preview)

		media_entry.find('etype')[0].style.backgroundImage = `url(${img_preview})`

		resolve(true)

	});
}

$this.spawn_file_unit = function(flpath)
{
	return
	const urlParams = new URLSearchParams({
		'action': 'get_lfs',
		'auth': 'ftp',
		'lfs_name': lst['flname'],
		'lfs': lst['path']
	});
	var media_entry = $(`
		<flist-entry class="media_entry" flpath="${lst['path']}" flname="${lst['flname']}">
			<etype file>
			</etype>
			<ename>${lst['flname']}</ename>
		</flist-entry>
	`)
}



$this.iterate_media = async function(ctrl)
{
	for (var lst of $this.dirlisting){
		// die if were told so
		if (ctrl.alive != true){return}


		if (lst['etype'] == 'img'){
			await $this.spawn_image_unit(lst['path'])
		}

		if (lst['etype'] == 'vid'){
			await $this.spawn_video_unit(lst['path'])
		}

		// $('mpool flist').append(media_entry);

		// important todo: this kinda works, but it'd be better to have a system for this
	}
	if (ctrl.alive != true){return}

	// kill self after iteration end
	// BUT don't do this if this iterator is dead
	ctrl.kill()
	$this.dirlisting = []
}



$this.medialist_iterator = function()
{
	return {
		launch: function(){
			if (this.abort){return}

			this.alive = true
			$this.iterate_media(this)
		},
		kill: function(){
			this.alive = false
			this.abort = true
		}
	}
}





$this.media_units_iteration = $this.medialist_iterator()
$this.list_media = async function(elm='')
{
	print('mpool list media')
	const fld_name = elm.getAttribute ? elm.getAttribute('fldpath') : elm;

	window.struct_fld = fld_name;
	$this.update_vis_path()
	$this.flush_preview_frames()

	// kill previous iterator
	$this.media_units_iteration.kill()
	$this.media_units_iteration = $this.medialist_iterator()

	$this.dirlisting = await $all.core.py_get(
		'poolsys/poolsys',
		{
			'action': 'list_media',
			'target': `${window.league}/${window.league_match}/${window.struct_fld}`
		},
		'json'
	)

	print('listed media:', $this.dirlisting)

	$('mpool flist').empty();
	$this.set_flist_view_type('grid');

	$('mpool flist').prepend(`
		<flist-entry fldpath="${window.league_match}" class="folder match" onclick="window.struct_fld = null; $this.list_match_struct(this)">
			<etype dir_up>
			</etype>
			<ename>../</ename>
		</flist-entry>
	`)

	$this.media_units_iteration.launch()
}




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
		(window.URL || window.webkitURL).revokeObjectURL($this.preview_cache[0].imgdata)
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







$this.temp_lies = async function(flpath)
{
	const media_preview = await $all.core.py_get(
		{
			'action': 'poolsys.load_media_preview',
			'media_path': flpath
		},
		'blob_url'
	)
	// print(media_preview)
	// return


	var media_entry = $(`
		<flist-entry class="media_entry" flpath="${flpath}" flname="${flpath.split('/').at(-1)}">
			<etype style="background-image: url(${media_preview})" img>
			</etype>
			<ename>${flpath.split('/').at(-1)}</ename>
		</flist-entry>
	`)

	$('mpool flist').append(media_entry)
}


$this.fm_cache = [];
$this.cache_fullres_media = function(url)
{
	if ($this.fm_cache.length > 16){
		(window.URL || window.webkitURL).revokeObjectURL($this.fm_cache[0])
		$this.fm_cache.shift()
	}
	$this.fm_cache.push(url)
}

$this.await_img_load = function(imgsrc)
{
	return new Promise(function(resolve, reject){
		var img = new Image();
		img.onload = function() {
			resolve(img)
		}
		img.onerror = function() {
			resolve(img)
		}
		img.src = imgsrc;
	});

}

$this.load_fullres_media = async function(elm)
{
	if (elm.nodeType != Node.ELEMENT_NODE){return}
	elm = elm.closest('flist-entry')
	// todo: this should work differently, probaly
	if (!elm.classList.contains('media_entry')){return}
	// delete existing preview from the page
	$('body > img#pic_fullres_preview').remove();
	$this.active_fullres_preview_elem = elm;
	$this.viewing_fullres = true;

	// if cache is present - pull from cache immediately
	const cache_attr = elm.getAttribute('img_cache');
	if ($this.fm_cache.includes(cache_attr)){
		$('body').append(`<img id="pic_fullres_preview" src="${cache_attr}">`);
		return
	}

	const media_path = elm.getAttribute('flpath');

	const tgt = $(`
		<img id="pic_fullres_preview" src="../assets/spinning_circle.svg">
	`);


	$('body').append(tgt)

	const fullres = await $all.core.py_get(
		'poolsys/poolsys',
		{
			'action': 'load_fullres_pic',
			'target': media_path
		},
		'blob_url'
	)

	// print(fullres)
	// Chrome still lags unlike firefox....
	// Chrome is prone to lagging when many tabs are open at once
	const img_l = await $this.await_img_load(fullres);
	img_l.id = 'pic_fullres_preview'
	tgt[0].replaceWith(img_l)
	// $('#pic_fullres_preview').remove()
	// img_l.id = 'pic_fullres_preview'
	// document.body.append(img_l)
	// update image src with loaded fullres preview
	// tgt[0].src = fullres
	// cache the image
	elm.setAttribute('img_cache', fullres)
	$this.cache_fullres_media(fullres)

}


$this.img_cycle_lr = function(arrow, elm)
{
	// todo: this can totally be better
	if (!$this.active_fullres_preview_elem || $this.viewing_fullres != true){return}
	if (arrow.keyCode == 37){
		$this.load_fullres_media($this.active_fullres_preview_elem.previousSibling)
	}
	if (arrow.keyCode == 39){
		$this.load_fullres_media($this.active_fullres_preview_elem.nextSibling)
	}
	$('flist-entry').removeClass('arrow_cycle_hint')
	$($this.active_fullres_preview_elem).addClass('arrow_cycle_hint')
}


$this.media_selection = [];
$this.add_media_entry_to_selection = function(evt, med)
{
	if (evt){evt.preventDefault()}
	const media_path = med.getAttribute('flpath');
	const media_name = media_path.split('/').at(-1);
	if (!$this.media_selection.includes(media_path) && media_path){
		$this.media_selection.push(media_path);
		med.classList.add('media_entry_selected');
		$('mpool dlq #dlq_list').append(`<div media_path="${media_path}" class="dlq_item">${media_name}</div>`);
	}else{
		// esle - remove from selection
		const item_index = $this.media_selection.indexOf(media_path);
		$this.media_selection.splice(item_index, 1);
		med.classList.remove('media_entry_selected');
		$(`mpool dlq #dlq_list .dlq_item[media_path="${media_path}"]`).remove();
	}
}


$this.clear_media_dl_queue = function()
{
	$this.media_selection = [];
	$('flist-entry').removeClass('media_entry_selected');
	$(`mpool dlq #dlq_list .dlq_item`).remove();
}


$this.update_vis_path = function()
{

	const ctext = (
		('root/')
		+
		(window.league ? (window.league + '/') : '')
		// (window.league ? (`<div vptype="league" class="vispath_fld">${window.league}</div><div class="vispath_separator">S</div>`) : '')
		+
		(window.league_match ? (window.league_match + '/') : '')
		// (window.league_match ? (`<div vptype="league_match" class="vispath_fld">${window.league_match}</div><div class="vispath_separator">S</div>`) : '')
		+
		(window.struct_fld ? (window.struct_fld + '/') : '')
		// (window.struct_fld ? (`<div vptype="struct_fld" class="vispath_fld">${window.struct_fld}</div>`) : '')
	)

	// $('#mpool_tobpar #vispath').text(`${window.league || ''}/${window.league_match || ''}/${window.struct_fld || ''}`)
	const cpath = (
		`<div vptype="root" class="vispath_fld">root</div><div class="vispath_separator">/</div>`
		+
		(window.league ? (`<div vptype="league" class="vispath_fld">${window.league}</div><div class="vispath_separator">/</div>`) : '')
		+
		(window.league_match ? (`<div vptype="league_match" class="vispath_fld">${window.league_match}</div><div class="vispath_separator">/</div>`) : '')
		+
		(window.struct_fld ? (`<div vptype="struct_fld" class="vispath_fld">${window.struct_fld}</div>`) : '')
	)
	$('#mpool_tobpar #vispath').html(cpath)

	// url
	print('update url')
	var queryParams = new URLSearchParams(window.location.search);
	queryParams.set('f', ctext);
	history.replaceState(null, null, '?'+queryParams.toString().replaceAll('%2F', '/'));
}

$this.vispath_clicker = async function(vp)
{
	const pathtype = vp.getAttribute('vptype')

	// also kill current iterator
	$this.media_units_iteration.kill()

	if (pathtype == 'root'){
		window.league = null
		window.league_match = null
		window.struct_fld = null
		await $this.load_root_dir()
	}
	if (pathtype == 'league'){
		window.league_match = null
		window.struct_fld = null
		await $this.list_league_matches(window.league)
	}
	if (pathtype == 'league_match'){
		window.struct_fld = null
		await $this.list_match_struct(window.league_match)
	}
	if (pathtype == 'struct_fld'){
		await $this.list_media(window.struct_fld)
	}
}




$this.select_all_in_folder = function(evt)
{
	// todo: this is ugly ?
	if (window.current_sys != 'main_pool'){return}

	if (evt){
		if (!(evt.ctrlKey && evt.keyCode == 65)){
			return
		}
		evt.preventDefault()
	}


	// if everything out of everything is selected - deselect everything
	const selected = $('flist-entry.media_entry.media_entry_selected').length
	const everything = $('flist-entry.media_entry').length

	if (selected == everything){
		// deselect
		for (var kms of document.querySelectorAll('flist-entry.media_entry.media_entry_selected')){
			$this.add_media_entry_to_selection(null, kms)
		}
		return
	}

	// deselect selected
	for (var kms of document.querySelectorAll('flist-entry.media_entry.media_entry_selected')){
		$this.add_media_entry_to_selection(null, kms)
	}
	// Select everything
	for (var kms of document.querySelectorAll('flist-entry.media_entry:not(.lfs_entry)')){
		$this.add_media_entry_to_selection(null, kms)
	}

}


$this.home_button = function()
{
	window.league = null;
	window.league_match = null;
	window.struct_fld = null;
	$this.update_vis_path()
	// if current sys name is main pool - don't reset the queue
	if (window.current_sys == 'main_pool'){
		$this.load_root_dir()
	}else{
		$this.module_loader()
	}
}


$this.download_image_from_fullres = function(evt, elm)
{
	evt.preventDefault()
	const flname = $(`flist-entry[img_cache="${elm.src}"]`).attr('flname');
	saveAs(elm.src, flname)
}
