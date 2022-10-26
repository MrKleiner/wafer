
if (!window.bootlegger){window.bootlegger = {}};

if (!window.bootlegger.main_pool){window.bootlegger.main_pool={}};

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



window.bootlegger.main_pool.module_loader = async function()
{
	await window.bootlegger.core.sysloader('main_pool', true);
	window.bootlegger.main_pool.load_root_dir()

}

window.bootlegger.main_pool.load_root_dir = async function()
{
	// list root shite
	const roots = await window.bootlegger.core.py_get(
		'poolsys/poolsys',
		{
			'action': 'list_leagues'
		},
		'json'
	)

	print('fuck this shit', roots)
	window.bootlegger.main_pool.update_vis_path()

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


window.bootlegger.main_pool.list_league_matches = async function(elm)
{
	const fld_name = elm.getAttribute('fldname');

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


window.bootlegger.main_pool.list_match_struct = async function(elm)
{
	// important todo: as was mentioned below this should be a system
	// and not just some random shit
	window.bootlegger.main_pool.dirlisting = [];
	const fld_name = elm.getAttribute('fldpath');

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




window.bootlegger.main_pool.list_media = async function(elm=null, manual=false)
{
	
	const fld_name = manual ? manual : elm.getAttribute('fldpath');

	window.struct_fld = fld_name;
	window.bootlegger.main_pool.update_vis_path()

	window.bootlegger.main_pool.dirlisting = await window.bootlegger.core.py_get(
		'poolsys/poolsys',
		{
			'action': 'list_media',
			'target': `${window.league}/${window.league_match}/${window.struct_fld}`
		},
		'json'
	)

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

	for (var lst of window.bootlegger.main_pool.dirlisting){
		console.time('Media Unit')
		// stupid
		// load preview first
		var media_preview = await window.bootlegger.core.py_get(
			'poolsys/poolsys',
			{
				'action': 'load_media_preview',
				'media_path': lst['path']
			},
			'blob_url'
		)
		print(media_preview)
		// return
		if (lst['lfs'] == true){
			const urlParams = new URLSearchParams({
				'action': 'get_lfs',
				'auth': 'ftp',
				'lfs_name': lst['flname'],
				'lfs': lst['path']
			});
			var media_entry = $(`
				<flist-entry class="media_entry lfs_entry" flpath="${lst['path']}" flname="${lst['flname']}">
					<etype novid>
					</etype>
					<a class="ename" href="htbin/lfs.py?${urlParams.toString()}">${lst['flname']}</a>
				</flist-entry>
			`)
		}else{
			if (lst['etype'] == 'file'){
				var media_entry = $(`
					<flist-entry class="media_entry" flpath="${lst['path']}" flname="${lst['flname']}">
						<etype file>
						</etype>
						<ename>${lst['flname']}</ename>
					</flist-entry>
				`)
			}else{
				var media_entry = $(`
					<flist-entry class="media_entry" flpath="${lst['path']}" flname="${lst['flname']}">
						<etype style="background-image: url(${media_preview})" img>
						</etype>
						<ename>${lst['flname']}</ename>
					</flist-entry>
				`)
			}

		}


		$('mpool flist').append(media_entry);

		// important todo: this kinda works, but it'd be better to have a system for this
		if (window.bootlegger.main_pool.dirlisting.length <= 0){return}

		// load preview
		console.timeEnd('Media Unit')

	}

	window.bootlegger.main_pool.dirlisting = []

	
}

window.bootlegger.main_pool.temp_lies = async function(flpath)
{
	const media_preview = await window.bootlegger.core.py_get(
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


window.bootlegger.main_pool.fm_cache = [];
window.bootlegger.main_pool.cache_fullres_media = function(url)
{
	if (window.bootlegger.main_pool.fm_cache.length > 16){
		(window.URL || window.webkitURL).revokeObjectURL(window.bootlegger.main_pool.fm_cache[0])
		window.bootlegger.main_pool.fm_cache.shift()
	}
	window.bootlegger.main_pool.fm_cache.push(url)
}

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

window.bootlegger.main_pool.load_fullres_media = async function(elm)
{

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
		<img id="pic_fullres_preview" src="../assets/spinning_circle.svg">
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


window.bootlegger.main_pool.update_vis_path = function()
{
	// $('#mpool_tobpar #vispath').text(`${window.league || ''}/${window.league_match || ''}/${window.struct_fld || ''}`)
	$('#mpool_tobpar #vispath').text(
		(window.league ? (window.league + '/') : '')
		+
		(window.league_match ? (window.league_match + '/') : '')
		+
		(window.struct_fld ? (window.struct_fld + '/') : '')
	)
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
	const selected = $('flist-entry.media_entry.media_entry_selected').length
	const everything = $('flist-entry.media_entry').length

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
