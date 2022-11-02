
// an array containg filepaths received from the server
$this.dirlisting = []



// ==================================================
// 						util
// ==================================================


// switch between grid and list layouts
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

// module load sequence
$this.module_loader = async function()
{
	print('start loading mpool')
	await $all.core.sysloader('main_pool', true);
	$this.restore_protocol()
	await $this.load_root_dir(false)
	await $this.go_dir_path()
}

// get path from the url and go there on page load 
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

// takes image url as an input and returns a fully loaded image element
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





// ==================================================
// 						Navigation
// ==================================================

// load the root directory of the entire FTP
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

// list subroot directories
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

// list dirs of the subroot dir
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













// ==================================================
// 					Media spawners
// ==================================================


// important todo: it looks like if an element with image url exists - it's being precached
// what are the limits of this ?
// how many elements at once can be precached ?
$this.video_bins = {}
$this.vidframes_cache = []
$this.spawn_video_unit = async function(vpath)
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
		const giga_info = preview_bin.read_file('index', 'json')
		const pframe_count = giga_info['preview_frame_count']
		$(`flist-entry[flpath="${vpath}"]`).attr('framecount', pframe_count)
		$this.video_bins[unit_id] = []
		for (var frame of range(pframe_count)){
			const imgu = preview_bin.read_file(`frn${frame+1}`, 'obj_url')
			$this.video_bins[unit_id].push(imgu)
			$this.vidframes_cache.push(await $this.await_img_load(imgu))
		}
		video_entry.find('etype')[0].style.backgroundImage = `url(${$this.video_bins[unit_id][0]})`
		resolve(true)

	});
}

// todo: this kinda belongs to the caching category
$this.flush_preview_frames = function()
{
	for (var rv in $this.video_bins){
		for (var fr of $this.video_bins[rv]){
			obj_url.revokeObjectURL(fr)
		}
	}
	for (var rv of $this.vidframes_cache){
		obj_url.revokeObjectURL(rv)
	}
}

// todo: collapse another multiplier
$this.vidscroll = function(evt, etgt)
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
	etgt.style.backgroundImage = `url(${$this.video_bins[pr_id][scroll]})`
}


$this.spawn_image_unit = async function(imgpath)
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












// ==================================================
// 					Iterators
// ==================================================

// an iterator object which iterates over the current dirlisting array
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

// controller of the iterator object
$this.medialist_iterator = function()
{
	return {
		launch: function(){
			if (this.alive == false){
				print('cant launch because not alive already')
				return
			}

			this.alive = true
			$this.iterate_media(this)
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
$this.media_units_iteration = $this.medialist_iterator()
$this.list_media = async function(elm='')
{
	print('mpool list media')
	const fld_name = elm.getAttribute ? elm.getAttribute('fldpath') : elm;

	window.struct_fld = fld_name;
	$this.update_vis_path()

	// remove video preview frames from browser cache
	// todo: actually keep them, like normal cache (aka not bigger than ...) ?
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

	// kill any existing iterators and spawn a new one
	$this.media_units_iteration.kill()
	$this.media_units_iteration = $this.medialist_iterator()

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







// ==================================================
// 			DOwnload video RMB. Todo: move to ft.js ?
// ==================================================
$this.video_dl = async function(evt, elem)
{
	evt.preventDefault()
	const dl_cmd = await $all.core.py_get(
		'poolsys/poolsys',
		{
			'action': 'get_dl_vid',
			'target': elem.getAttribute('flpath')
		},
		'json'
	)

	if (dl_cmd.status == 'lizard'){
		window.open(dl_cmd.cmd)
	}
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
		<img draggable="false" id="pic_fullres_preview" src="../assets/spinning_circle.svg">
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
	img_l.setAttribute('draggable', 'false')
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
	const selected = $('flist-entry.media_entry.media_entry_selected.mde_img').length
	const everything = $('flist-entry.media_entry.mde_img').length

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









// ==================================================
// 					visual path stuff
// ==================================================
$this.update_vis_path = function()
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
	$this.current_pool_dir = ctext.replace('root/', '')

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













// ==================================================
// 					Restore protocol
// ==================================================
$this.restore_protocol = function()
{
	// no hash no shit
	var rst_protocol = window.localStorage.getObj('restore_protocol')
	if (!rst_protocol.rst_hash || rst_protocol.collapsed == true){
		print('Restore Protocol:', 'no valid hash found or the entry was collapsed')
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






















// ==================================================
// 					Cool webm previews
// ==================================================

// this is needed, because preventDefault is called whenever spacebar or arrows are pressed
// this lets the system check whether the webm preview is actually active or not
$this.viewing_webm = false
$this.open_webm_preview = async function(elm)
{
	const flpath = elm.closest('flist-entry').getAttribute('flpath')

	// indicate loading
	$('body #webm_preview').remove()
	$('body').append(`
		<div id="webm_preview">
			<div id="webm_vid_name">${elm.getAttribute('flname')}</div>
			<div id="webm_video_player">
				<img id="webm_video_loading_status" src="../assets/spinning_circle.svg">
				<video class="core_hidden_opacity" ontimeupdate="$this.show_video_time(this)"></video>
				<input value="50" min="0" max="100" type="range" id="volume_slider">
			</div>
			<div id="webm_timeline_stats">
				<div id="timeline_timecode">00:00:00:00</div>
				<div id="timeline_ctrl">
					<div class="start_stop" id="tl_play">
						<img draggable="false" src="../../assets/play_btn.svg">
					</div>
					<div class="start_stop" id="tl_stop">
						<img draggable="false" src="../../assets/pause_btn.svg">
					</div>
				</div>
			</div>
			<div id="webm_video_waveform"></div>
		</div>
	`)

	// load video and audio
	const webm_vid =  await $all.core.py_get(
		'poolsys/poolsys',
		{
			'action': 'get_webm',
			'vidpath': flpath
		},
		'blob_url'
	)
	// load video and audio
	const webm_audio =  await $all.core.py_get(
		'poolsys/poolsys',
		{
			'action': 'get_webm_audio',
			'vidpath': flpath
		},
		'blob'
	)
	print('Done loading webm shite', webm_vid, webm_audio)
	
	// store the video selector somewhere	
	const fuckoff = document.querySelector('#webm_video_player video')
	fuckoff.src = webm_vid;
	fuckoff.volume = 0.5;
	$this.current_webm_vid = fuckoff;
	// fuckoff, HOW CAN VIDEO LENGTH BE FUCKING INFINITY ??????
	fuckoff.currentTime = 60*(60*900)
	await fuckoff.play()

	// create waveform object
	$this.wave_ctrl = WaveSurfer.create({
		container: '#webm_video_waveform',
		// waveColor: '#267954',
		waveColor: '#1D5D40',
		progressColor: '#4BF2A7',
		fillParent: true,
		scrollParent: false,
		responsive: true
	});
	$this.wave_ctrl.loadBlob(webm_audio);
	
	// audio is loaded lastly, which means that it's a concluding step
	$this.wave_ctrl.on('ready', function () {
		// at this point everything is loaded
		// now it has to be set up

		// the audio is not actually coming from the waveform...
		// therefore it has to be silent
		$this.wave_ctrl.setVolume(0);
		// scroll webm video to the start
		fuckoff.currentTime = 0;

		// unveal everything in the gui
		$('#webm_preview img#webm_video_loading_status').remove()
		fuckoff.classList.remove('core_hidden_opacity')

		// start playing video and waveform
		$this.wave_ctrl.play();
		fuckoff.play();

		// indicate that viewing is active
		// important todo: it has to be possible to cancel the loading
		// this is here so that nobody can fuckup the sync due to audio/video loading slower
		$this.viewing_webm = true
	});
}



// navigation
$this.nav_webm_audio = function(evt, elm)
{
	// Get bbox relative to viewport
	const rect = elm.getBoundingClientRect()

	// get total length of the video in seconds
	// todo: store this in the window for faster access
	const vid = document.querySelector('#webm_video_player video')

	// Mouse position relative to element
	const current_x = Math.abs(evt.clientX - rect.left);
	// current / total = current percent progress
	const scroll = vid.duration * (current_x / rect.width)
	print('Scroll is', {
		'clientx': evt.clientX,
		'rectleft': rect.left,
		'duration': vid.duration,
		'scroll': scroll
	})
	vid.currentTime = scroll
}


// running timecode
// stolen from stack overflow
// GOD SAVE THE Q- STACK OVERFLOW

/*
let totalSeconds = 28565;
let hours = Math.floor(totalSeconds / 3600);
totalSeconds %= 3600;
let minutes = Math.floor(totalSeconds / 60);
let seconds = totalSeconds % 60;

console.log("hours: " + hours);
console.log("minutes: " + minutes);
console.log("seconds: " + seconds);

// If you want strings with leading zeroes:
minutes = String(minutes).padStart(2, "0");
hours = String(hours).padStart(2, "0");
seconds = String(seconds).padStart(2, "0");
console.log(hours + ":" + minutes + ":" + seconds);
*/

$this.show_video_time = function(vid)
{
	const mkmsec = vid.currentTime

	let totalSeconds = vid.currentTime;
	let hours = Math.floor(totalSeconds / 3600);
	totalSeconds %= 3600;
	let minutes = Math.floor(totalSeconds / 60);
	let seconds = totalSeconds % 60;

	const msec = str(mkmsec.toFixed(2)).split('.').at(-1).zfill(2)

	const tcode = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(parseInt(seconds)).padStart(2, '0')}:${String(msec).padStart(2, '0')}`

	document.querySelector('#webm_preview #timeline_timecode').innerText = tcode
}

$this.pause_webm = function()
{
	$this.wave_ctrl.pause()
	$this.current_webm_vid.pause()
}

$this.play_webm = function()
{
	$this.wave_ctrl.play()
	$this.current_webm_vid.play()
}

$this.toggle_webm_play = function(evt)
{
	if (!(evt.keyCode == 32) || $this.viewing_webm != true){return}

	evt.preventDefault()

	if ($this.current_webm_vid.paused){
		$this.wave_ctrl.play()
		$this.current_webm_vid.play()
	}else{
		$this.wave_ctrl.pause()
		$this.current_webm_vid.pause()
	}
}

$this.webm_skip_lr = async function(evt)
{
	// don't do shit if those aren't the LR buttons
	if (!(evt.keyCode == 37) && !(evt.keyCode == 39) || $this.viewing_webm != true){return}
	evt.preventDefault()

	// how many seconds to skip
	var skip_sec = 5.0

	// in which way to skip
	const skip_offs = (evt.keyCode == 37) ? (skip_sec * -1) : skip_sec

	// FUCK JS
	const real_time = Math.max($this.current_webm_vid.currentTime + skip_offs, 0)
	// basically, fuck js v2
	const wsf_loop = (($this.wave_ctrl.getCurrentTime() == $this.wave_ctrl.getDuration()) && skip_offs != (skip_sec * -1)) ? 0 : real_time

	// pause all
	await $this.wave_ctrl.pause()
	await $this.current_webm_vid.pause()

	// skip
	// await $this.wave_ctrl.skip(skip_offs)
	$this.current_webm_vid.currentTime = real_time

	print('Honestly fuckoff with this...', $this.current_webm_vid.currentTime, $this.wave_ctrl.getCurrentTime())
	// unpause
	$this.wave_ctrl.play(wsf_loop)
	$this.current_webm_vid.play()
	
}

$this.close_webm_preview = function(evt)
{
	// only trigger this if the preview is actually active
	if (!(evt.keyCode == 27) || $this.viewing_webm != true){return}

	// indicate that the webm preview is no longer active
	$this.viewing_webm = false;
	// delete webm video from cache
	obj_url.revokeObjectURL($this.current_webm_vid.src)
	// kill waveform
	$this.wave_ctrl.destroy()
	// kill overlay
	$('#webm_preview').remove()
}

$this.mwheel_adjust_volume = function(evt)
{
	if ($this.viewing_webm != true){return}

	evt.preventDefault()
	evt.stopPropagation()

	const sld = document.querySelector('#volume_slider')

	if (evt.deltaY < 0){
		sld.valueAsNumber += 5;
	}else{
		sld.valueAsNumber -= 5;
	}

	$this.current_webm_vid.volume = sld.valueAsNumber / 100
}













// todo: move it to event binds
// document.addEventListener('mousemove', tr_event => {
// 	if ($this.drag_handle){
// 		$this.handle_move(tr_event)
// 	}
// });


$this.handle_unbind = function()
{
	$this.drag_handle = null;
}

$this.handle_stick = function(tr_event, schandle)
{
	$this.handle_set_from_slider(schandle, tr_event);
	$this.drag_handle = schandle.closest('#sc_body').querySelector('#sc_handle');
}

$this.handle_move = function(evt)
{
	if (!$this.drag_handle){return}
	const sc_root = $this.drag_handle.closest('#sc_body');
	const handle = $this.drag_handle;
	const sc_root_dims = getComputedStyle(sc_root);
	const sc_root_rect = sc_root.getBoundingClientRect();
	
	const offs = evt.clientY - sc_root_rect.top;
	// and so a wise man has spoken: thy function calls are expensive
	const clamped = Math.min(Math.max(offs, 35), sc_root_rect.height - 35)
	console.log(clamped)
	$this.drag_handle.style.top = clamped.toString() + 'px'
}

$this.handle_set_from_slider = function(sld, evt)
{
	const sl_root = sld.closest('#sc_body')
	const handle = sl_root.querySelector('#sc_handle');

	const sc_root_dims = getComputedStyle(sl_root);
	const sc_root_rect = sl_root.getBoundingClientRect();
	
	const offs = evt.clientY - sc_root_rect.top;
	// and so a wise man has spoken: thy function calls are expensive
	const clamped = Math.min(Math.max(offs, 35), sc_root_rect.height - 35)
	handle.style.top = clamped.toString() + 'px'
}

$this.handle_set_abs = function(slider, perc=0)
{
	const sl_root = slider.closest('#sc_body')
	const handle = sl_root.querySelector('#sc_handle');

	const sc_root_dims = getComputedStyle(sl_root);
	const sc_root_rect = sl_root.getBoundingClientRect();
	
	const offs = sc_root_rect.height * perc;
	// and so a wise man has spoken: thy function calls are expensive
	const clamped = Math.min(Math.max(offs, 35), sc_root_rect.height - 35)
	handle.style.top = clamped.toString() + 'px'
}


/*

	"mousedown": [
		{
			"selector": "#webm_preview #sc_handle, #sc_body",
			"function": "console.log",
			"pass_event": true,
			"pass_element": true,
			"pass_params": ""
		}
	],
	"mouseup": [
		{
			"selector": "body",
			"function": "$this.vidscroll",
			"pass_event": true,
			"pass_element": true,
			"pass_params": ""
		}
	],*/