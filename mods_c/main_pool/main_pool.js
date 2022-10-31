
if (!window.bootlegger){window.bootlegger = {}};

if (!window.bootlegger.main_pool){window.bootlegger.main_pool={}};

// an array containg filepaths received from the server
window.bootlegger.main_pool.dirlisting = []



// ==================================================
// 						util
// ==================================================


// switch between grid and list layouts
window.bootlegger.main_pool.set_flist_view_type = function(tp='list')
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

// module load sequence
window.bootlegger.main_pool.module_loader = async function()
{
	print('start loading mpool')
	await window.bootlegger.core.sysloader('main_pool', true);
	window.bootlegger.main_pool.restore_protocol()
	await window.bootlegger.main_pool.load_root_dir(false)
	await window.bootlegger.main_pool.go_dir_path()
}

// get path from the url and go there on page load 
window.bootlegger.main_pool.go_dir_path = async function()
{
	print('go dir path')
	const urlParams = new URLSearchParams(window.location.search);
	const load_loc = urlParams.get('f');
	const paths = load_loc.trim().strip('/').split('/')

	paths[1] ? (await window.bootlegger.main_pool.list_league_matches(paths[1])) : null
	print('godir 1')
	paths[2] ? (await window.bootlegger.main_pool.list_match_struct(paths[2])) : null
	print('godir 2')
	paths[3] ? (await window.bootlegger.main_pool.list_media(paths[3])) : null
}

// takes image url as an input and returns a fully loaded image element
window.bootlegger.main_pool.await_img_load = function(imgsrc)
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





// ==================================================
// 						Navigation
// ==================================================

// load the root directory of the entire FTP
window.bootlegger.main_pool.load_root_dir = async function(doup=true)
{
	print('mpool load root dir')
	window.bootlegger.main_pool.media_units_iteration.kill()
	// list root shite
	const roots = await window.bootlegger.core.py_get(
		'poolsys/poolsys',
		{
			'action': 'list_leagues'
		},
		'json'
	)
	print('mpool loaded root dir')

	print('fuck this shit', roots)
	doup ? window.bootlegger.main_pool.update_vis_path() : null
	// window.bootlegger.main_pool.update_vis_path()

	$('mpool flist').empty();
	window.bootlegger.main_pool.set_flist_view_type('list');
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

// list subroot directories
window.bootlegger.main_pool.list_league_matches = async function(elm='')
{
	window.bootlegger.main_pool.media_units_iteration.kill()
	print('mpool list matches')
	const fld_name = elm.getAttribute ? elm.getAttribute('fldname') : elm;

	window.league = fld_name;
	window.bootlegger.main_pool.update_vis_path()


	const full_root = (await window.bootlegger.core.load_dbfile('root.json', 'json'))['root_path']

	const subroot_flds = await window.bootlegger.core.py_get(
		'poolsys/poolsys',
		{
			'action': 'list_league_matches',
			'league_name': fld_name
		},
		'json'
	)

	$('mpool flist').empty();
	window.bootlegger.main_pool.set_flist_view_type('list');

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
		<flist-entry class="folder" onclick="window.league = null; window.bootlegger.main_pool.load_root_dir()">
			<etype folder>
			</etype>
			<ename>../</ename>
		</flist-entry>
	`)

}

// list dirs of the subroot dir
window.bootlegger.main_pool.list_match_struct = async function(elm='')
{
	print('mpool list match struct')
	// important todo: as was mentioned below this should be a system
	// and not just some random shit
	// update: this is SOME sort of system, but still not what we need
	window.bootlegger.main_pool.media_units_iteration.kill()
	window.bootlegger.main_pool.dirlisting = [];
	const fld_name = elm.getAttribute ? elm.getAttribute('fldpath') : elm;

	window.league_match = fld_name;
	window.bootlegger.main_pool.update_vis_path()

	const dirlisting = await window.bootlegger.core.py_get(
		'poolsys/poolsys',
		{
			'action': 'list_match_struct',
			'match_name': `${window.league}/${window.league_match}`
		},
		'json'
	)

	print('listed match:', dirlisting)

	$('mpool flist').empty();
	window.bootlegger.main_pool.set_flist_view_type('list');

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
		<flist-entry fldname="${window.league}" class="folder" onclick="window.league_match = null; window.bootlegger.main_pool.list_league_matches(this)">
			<etype folder>
			</etype>
			<ename>../</ename>
		</flist-entry>
	`)
}













// ==================================================
// 					Media spawners
// ==================================================


// important todo: it looks like if an element with image url exists - it's being precached
// what are the limits of this ?
// how many elements at once can be precached ?
window.bootlegger.main_pool.video_bins = {}
window.bootlegger.main_pool.vidframes_cache = []
window.bootlegger.main_pool.spawn_video_unit = async function(vpath)
{
	return new Promise(async function(resolve, reject){

		const fname = vpath.split('/').at(-1).trim()
		const unit_id = lizard.rndwave(32, 'def')

		const video_entry = $(`
			<flist-entry unit_id="${unit_id}" class="media_entry lfs_entry mde_vid" flpath="${vpath}" flname="${fname}">
				<etype style="background-image: url(./assets/spinning_circle.svg)" vid>
				</etype>
				<ename>${fname}</ename>
			</flist-entry>
		`)
		// todo: is there a smarter way of managing this?
		// for now the existing entry is replaced with a new one
		$(`mpool flist flist-entry[flname="${fname}"]`).remove()
		$('mpool flist').append(video_entry)

		var video_preview = window.bootlegger.main_pool.preview_cache_pull(vpath)

		if (!video_preview){
			var video_preview = await window.bootlegger.core.py_get(
				'poolsys/poolsys',
				{
					'action': 'load_video_preview',
					'video_path': vpath
				},
				'buffer'
			)
			window.bootlegger.main_pool.preview_cache_add(vpath, video_preview)
		}

		
		const preview_bin = new window.gigabin(video_preview)
		const giga_info = preview_bin.read_file('index', 'json')
		const pframe_count = giga_info['preview_frame_count']
		$(`flist-entry[flpath="${vpath}"]`).attr('framecount', pframe_count)
		window.bootlegger.main_pool.video_bins[unit_id] = []
		for (var frame of range(pframe_count)){
			const imgu = preview_bin.read_file(`frn${frame+1}`, 'obj_url')
			window.bootlegger.main_pool.video_bins[unit_id].push(imgu)
			window.bootlegger.main_pool.vidframes_cache.push(await window.bootlegger.main_pool.await_img_load(imgu))
		}
		video_entry.find('etype')[0].style.backgroundImage = `url(${window.bootlegger.main_pool.video_bins[unit_id][0]})`
		resolve(true)

	});
}

// todo: this kinda belongs to the caching category
window.bootlegger.main_pool.flush_preview_frames = function()
{
	for (var rv in window.bootlegger.main_pool.video_bins){
		for (var fr of window.bootlegger.main_pool.video_bins[rv]){
			obj_url.revokeObjectURL(fr)
		}
	}
	for (var rv of window.bootlegger.main_pool.vidframes_cache){
		obj_url.revokeObjectURL(rv)
	}
}

// todo: collapse another multiplier
window.bootlegger.main_pool.vidscroll = function(evt, etgt)
{
	// element
	const flist_entry = etgt.closest('flist-entry')

	// Get bbox relative to viewport
	const pr_id = flist_entry.getAttribute('unit_id')
	const rect = etgt.getBoundingClientRect()

	// get frame count
	const prf = flist_entry.getAttribute('framecount')

	// Mouse position relative to element
	const current_x = Math.abs(evt.clientX - rect.left);
	// current / total = current percent progress
	const scroll = int(prf * (current_x / rect.width))
	etgt.style.backgroundImage = `url(${window.bootlegger.main_pool.video_bins[pr_id][scroll]})`
}


window.bootlegger.main_pool.spawn_image_unit = async function(imgpath)
{
	return new Promise(async function(resolve, reject){
		// todo: the split solution is just rubbish
		const fname = imgpath.split('/').at(-1).trim()
		// todo: class mde_img goes against consistency
		// either mark element with img/vid/file attribute as the whole
		// or comeup with something better
		const media_entry = $(`
			<flist-entry class="media_entry mde_img" flpath="${imgpath}" flname="${fname}">
				<etype style="background-image: url(./assets/spinning_circle.svg)" img>
				</etype>
				<ename>${fname}</ename>
			</flist-entry>
		`)
		// todo: is there a smarter way of managing this?
		// for now the existing entry is replaced with a new one
		$(`mpool flist flist-entry[flname="${fname}"]`).remove()
		$('mpool flist').append(media_entry)

		// try pulling shit from cache
		var img_preview = window.bootlegger.main_pool.preview_cache_pull(imgpath)

		// else - load from server
		if (!img_preview){
			var img_preview = await window.bootlegger.core.py_get(
				'poolsys/poolsys',
				{
					'action': 'load_image_preview',
					'image_path': imgpath
				},
				'blob_url'
			)
			window.bootlegger.main_pool.preview_cache_add(imgpath, img_preview)
		}

		print(img_preview)

		media_entry.find('etype')[0].style.backgroundImage = `url(${img_preview})`

		resolve(true)

	});
}

window.bootlegger.main_pool.spawn_file_unit = function(flpath)
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












// ==================================================
// 					Iterators
// ==================================================

// an iterator object which iterates over the current dirlisting array
window.bootlegger.main_pool.iterate_media = async function(ctrl)
{
	for (var lst of window.bootlegger.main_pool.dirlisting){
		// die if were told so
		if (ctrl.alive != true){return}


		if (lst['etype'] == 'img'){
			await window.bootlegger.main_pool.spawn_image_unit(lst['path'])
		}

		if (lst['etype'] == 'vid'){
			await window.bootlegger.main_pool.spawn_video_unit(lst['path'])
		}

		// $('mpool flist').append(media_entry);

		// important todo: this kinda works, but it'd be better to have a system for this
	}
	if (ctrl.alive != true){return}

	// kill self after iteration end
	// BUT don't do this if this iterator is dead
	ctrl.kill()
	window.bootlegger.main_pool.dirlisting = []
}

// controller of the iterator object
window.bootlegger.main_pool.medialist_iterator = function()
{
	return {
		launch: function(){
			if (this.alive == false){
				print('cant launch because not alive already')
				return
			}

			this.alive = true
			window.bootlegger.main_pool.iterate_media(this)
		},
		kill: function(){
			this.alive = false
			this.abort = true
		}
	}
}









// ==================================================
// 			directory file listing gateway
// ==================================================
window.bootlegger.main_pool.media_units_iteration = window.bootlegger.main_pool.medialist_iterator()
window.bootlegger.main_pool.list_media = async function(elm='')
{
	print('mpool list media')
	const fld_name = elm.getAttribute ? elm.getAttribute('fldpath') : elm;

	window.struct_fld = fld_name;
	window.bootlegger.main_pool.update_vis_path()

	// remove video preview frames from browser cache
	// todo: actually keep them, like normal cache (aka not bigger than ...) ?
	window.bootlegger.main_pool.flush_preview_frames()

	// kill previous iterator
	window.bootlegger.main_pool.media_units_iteration.kill()
	window.bootlegger.main_pool.media_units_iteration = window.bootlegger.main_pool.medialist_iterator()

	window.bootlegger.main_pool.dirlisting = await window.bootlegger.core.py_get(
		'poolsys/poolsys',
		{
			'action': 'list_media',
			'target': `${window.league}/${window.league_match}/${window.struct_fld}`
		},
		'json'
	)

	// kill any existing iterators and spawn a new one
	window.bootlegger.main_pool.media_units_iteration.kill()
	window.bootlegger.main_pool.media_units_iteration = window.bootlegger.main_pool.medialist_iterator()

	print('listed media:', window.bootlegger.main_pool.dirlisting)

	$('mpool flist').empty();
	window.bootlegger.main_pool.set_flist_view_type('grid');

	$('mpool flist').prepend(`
		<flist-entry fldpath="${window.league_match}" class="folder match" onclick="window.struct_fld = null; window.bootlegger.main_pool.list_match_struct(this)">
			<etype dir_up>
			</etype>
			<ename>../</ename>
		</flist-entry>
	`)

	window.bootlegger.main_pool.media_units_iteration.launch()
}




















window.bootlegger.main_pool.load_fullres_media = async function(elm)
{
	if (elm.nodeType != Node.ELEMENT_NODE){return}
	elm = elm.closest('flist-entry')
	// todo: this should work differently, probaly
	if (!elm.classList.contains('media_entry')){return}
	// delete existing preview from the page
	$('body > img#pic_fullres_preview').remove();
	window.bootlegger.main_pool.active_fullres_preview_elem = elm;
	window.bootlegger.main_pool.viewing_fullres = true;

	// if cache is present - pull from cache immediately
	const cache_attr = elm.getAttribute('img_cache');
	if (window.bootlegger.main_pool.fm_cache.includes(cache_attr)){
		$('body').append(`<img id="pic_fullres_preview" src="${cache_attr}">`);
		return
	}

	const media_path = elm.getAttribute('flpath');

	const tgt = $(`
		<img draggable="false" id="pic_fullres_preview" src="../assets/spinning_circle.svg">
	`);


	$('body').append(tgt)

	const fullres = await window.bootlegger.core.py_get(
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
	const img_l = await window.bootlegger.main_pool.await_img_load(fullres);
	img_l.id = 'pic_fullres_preview'
	img_l.setAttribute('draggable', 'false')
	tgt[0].replaceWith(img_l)
	// $('#pic_fullres_preview').remove()
	// img_l.id = 'pic_fullres_preview'
	// document.body.append(img_l)
	// update image src with loaded fullres preview
	// tgt[0].src = fullres
	// cache the image
	elm.setAttribute('img_cache', fullres)
	window.bootlegger.main_pool.cache_fullres_media(fullres)

}


window.bootlegger.main_pool.img_cycle_lr = function(arrow, elm)
{
	// todo: this can totally be better
	if (!window.bootlegger.main_pool.active_fullres_preview_elem || window.bootlegger.main_pool.viewing_fullres != true){return}
	if (arrow.keyCode == 37){
		window.bootlegger.main_pool.load_fullres_media(window.bootlegger.main_pool.active_fullres_preview_elem.previousSibling)
	}
	if (arrow.keyCode == 39){
		window.bootlegger.main_pool.load_fullres_media(window.bootlegger.main_pool.active_fullres_preview_elem.nextSibling)
	}
	$('flist-entry').removeClass('arrow_cycle_hint')
	$(window.bootlegger.main_pool.active_fullres_preview_elem).addClass('arrow_cycle_hint')
}


window.bootlegger.main_pool.media_selection = [];
window.bootlegger.main_pool.add_media_entry_to_selection = function(evt, med)
{
	if (evt){evt.preventDefault()}
	const media_path = med.getAttribute('flpath');
	const media_name = media_path.split('/').at(-1);
	if (!window.bootlegger.main_pool.media_selection.includes(media_path) && media_path){
		window.bootlegger.main_pool.media_selection.push(media_path);
		med.classList.add('media_entry_selected');
		$('mpool dlq #dlq_list').append(`<div media_path="${media_path}" class="dlq_item">${media_name}</div>`);
	}else{
		// esle - remove from selection
		const item_index = window.bootlegger.main_pool.media_selection.indexOf(media_path);
		window.bootlegger.main_pool.media_selection.splice(item_index, 1);
		med.classList.remove('media_entry_selected');
		$(`mpool dlq #dlq_list .dlq_item[media_path="${media_path}"]`).remove();
	}
}


window.bootlegger.main_pool.clear_media_dl_queue = function()
{
	window.bootlegger.main_pool.media_selection = [];
	$('flist-entry').removeClass('media_entry_selected');
	$(`mpool dlq #dlq_list .dlq_item`).remove();
}



window.bootlegger.main_pool.select_all_in_folder = function(evt)
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
	const selected = $('flist-entry.media_entry.media_entry_selected.mde_img').length
	const everything = $('flist-entry.media_entry.mde_img').length

	if (selected == everything){
		// deselect
		for (var kms of document.querySelectorAll('flist-entry.media_entry.media_entry_selected')){
			window.bootlegger.main_pool.add_media_entry_to_selection(null, kms)
		}
		return
	}

	// deselect selected
	for (var kms of document.querySelectorAll('flist-entry.media_entry.media_entry_selected')){
		window.bootlegger.main_pool.add_media_entry_to_selection(null, kms)
	}
	// Select everything
	for (var kms of document.querySelectorAll('flist-entry.media_entry:not(.lfs_entry)')){
		window.bootlegger.main_pool.add_media_entry_to_selection(null, kms)
	}

}


window.bootlegger.main_pool.home_button = function()
{
	window.league = null;
	window.league_match = null;
	window.struct_fld = null;
	window.bootlegger.main_pool.update_vis_path()
	// if current sys name is main pool - don't reset the queue
	if (window.current_sys == 'main_pool'){
		window.bootlegger.main_pool.load_root_dir()
	}else{
		window.bootlegger.main_pool.module_loader()
	}
}


window.bootlegger.main_pool.download_image_from_fullres = function(evt, elm)
{
	evt.preventDefault()
	const flname = $(`flist-entry[img_cache="${elm.src}"]`).attr('flname');
	saveAs(elm.src, flname)
}









// ==================================================
// 					visual path stuff
// ==================================================
window.bootlegger.main_pool.update_vis_path = function()
{
	// this goes to the url and global context
	const ctext = (
		('root/')
		+
		(window.league ? (window.league + '/') : '')
		+
		(window.league_match ? (window.league_match + '/') : '')
		+
		(window.struct_fld ? window.struct_fld : '')
	)
	window.bootlegger.main_pool.current_pool_dir = ctext.replace('root/', '')

	// and this appears on the page
	const cpath = (
		`<div vptype="root" class="vispath_fld">root</div><div class="vispath_separator">/</div>`
		+
		(window.league ? (`<div vptype="league" class="vispath_fld">${window.league}</div><div class="vispath_separator">/</div>`) : '')
		+
		(window.league_match ? (`<div vptype="league_match" class="vispath_fld">${window.league_match}</div><div class="vispath_separator">/</div>`) : '')
		+
		(window.struct_fld ? (`<div vptype="struct_fld" class="vispath_fld">${window.struct_fld}</div>`) : '')
	)

	// page visuals
	$('#mpool_tobpar #vispath').html(cpath)

	// url
	print('update url')
	var queryParams = new URLSearchParams(window.location.search);
	queryParams.set('f', ctext);
	// important todo: use URL decode instead of simple replacement stuff
	window.history.replaceState(null, null, '?'+queryParams.toString().replaceAll('%2F', '/'));

	// restore point stuff
	const rst_path = window.localStorage.getObj('restore_protocol').rst_dest
	print('PLEASE NO', `root/${rst_path}`.strip('/'), ctext.strip('/'))
	if (`root/${rst_path}`.strip('/') == ctext.strip('/')){
		$('dlq #dlq_list .dlq_item.restore_point .dest').addClass('rst_dest_valid')
	}else{
		$('dlq #dlq_list .dlq_item.restore_point .dest').removeClass('rst_dest_valid')
	}
}

window.bootlegger.main_pool.vispath_clicker = async function(vp)
{
	const pathtype = vp.getAttribute('vptype')

	// also kill current iterator
	window.bootlegger.main_pool.media_units_iteration.kill()

	if (pathtype == 'root'){
		window.league = null
		window.league_match = null
		window.struct_fld = null
		await window.bootlegger.main_pool.load_root_dir()
	}
	if (pathtype == 'league'){
		window.league_match = null
		window.struct_fld = null
		await window.bootlegger.main_pool.list_league_matches(window.league)
	}
	if (pathtype == 'league_match'){
		window.struct_fld = null
		await window.bootlegger.main_pool.list_match_struct(window.league_match)
	}
	if (pathtype == 'struct_fld'){
		await window.bootlegger.main_pool.list_media(window.struct_fld)
	}
}








// ==================================================
// 					Restore protocol
// ==================================================
window.bootlegger.main_pool.restore_protocol = function()
{
	// no hash no shit
	var rst_protocol = window.localStorage.getObj('restore_protocol')
	if (!rst_protocol.rst_hash){
		print('Restore Protocol:', 'no valid hash found')
		return
	}

	// recreate queue
	print('RESTORE POINT EXISTS !')

	$('dlq #dlq_list').append(`
		<div class="dlq_item lfs_item restore_point">
			<div class="lfs_item_name_sizer">${rst_protocol.rst_name}</div>
			<div class="lfs_progress"></div>
			<div class="lfs_item_name">${rst_protocol.rst_name}</div>
			<div class="rst_point_warning_info">
				<div class="warn_entry">Target Path:</div>
				<div class="warn_entry dest">${rst_protocol.rst_dest}</div>
				<div class="warn_entry">Checksum:</div>
				<div class="warn_entry checksum">${rst_protocol.rst_hash}</div>
				<div class="warn_entry">Byte Offset: ${rst_protocol.rst_offs}</div>
			</div>
			<div class="rst_point_warning"></div>
		</div>
	`);
}