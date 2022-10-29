
$this.file_upload_q = []
// $this.lock_queue = false;
// dont forget to lock this after the file upload has started
function file_pool_drop_react(evt)
{
	evt.preventDefault()
	file_pool_drag_leave_react()

	// todo: does it really has to be const?
	const item_list = evt.dataTransfer.items || evt.dataTransfer.files;

	// iterate over shit and add them to the raw queue
	for (var fl of item_list){
		// if ($this.lock_queue == true){return}
		if (fl.kind && fl.kind == 'file'){
			const getf = fl.getAsFile()
			$this.file_upload_q.push({
				'file': getf,
				'processed': false,
				'dest': `${window.league}/${window.league_match}/${window.struct_fld}`,
				'live_shift': 0
			})
			$('dlq #dlq_list').append(`<div upl_name="${getf.name}" class="dlq_item">${getf.name}</div>`)
		}
		if (!fl.kind){
			$this.file_upload_q.push({
				'file': fl,
				'processed': false,
				'dest': `${window.league}/${window.league_match}/${window.struct_fld}`,
				'live_shift': 0
			})
			$('dlq #dlq_list').append(`<div upl_name="${fl.name}" class="dlq_item">${fl.name}</div>`)
		}
	}

	$this.upload_queue.resume()
}



// this is needed to prevent browser from opening dragged files
// YES, this has to be done when the drop has just starter and NOT when released...
// it appears that preventDefault has to be EVERYWHERE
function file_pool_hover_react(evt)
{
	evt.preventDefault();
}

function file_pool_drag_enter_react()
{
	$('body').prepend(`
		<div id="indicate_can_drop_files">
			<div id="indicate_can_drop_files_icon"></div>
		</div>
	`)
}

function file_pool_drag_leave_react()
{
	$('#indicate_can_drop_files').remove();
}





// mt either buffer or blob
$this.read_file_slice = async function(file, offs, mt='buffer')
{
	return new Promise(function(resolve, reject){
		var reader = new FileReader();
	    reader.readAsArrayBuffer(file.slice(offs[0], offs[1]), 'UTF-8');
	    reader.onload = function (evt) {
			if (mt == 'buffer'){
				resolve(reader.result)
			}else{
				const boobs = new Blob([reader.result], {type: file.type});
				resolve(boobs)
			}
		};
	});
}

// takes file as an input
$this.hash_file = async function(inp_file, chunk_sizemb=50)
{
	// create hash object
	var sha256 = CryptoJS.algo.SHA256.create();

	// store current offset
	var offs = 0
	const chunk_size = (1024**2)*chunk_sizemb

	// keep reading chunks
	while (true){
		// read slice as array buffer
		var fl_slice = await $this.read_file_slice(inp_file, [offs, offs+chunk_size])
		// bytelength = length in bytes of the resulting slice
		// break if it's zero
		if (fl_slice.byteLength <= 0){break}
		// stupid fucking shit WordArray. No documentation for this AT FUCKING ALL
		// the line below is fucking priceless, it's IMPORTANT AS FUCK
		// the cryptoJS shit only accepts EITHER strings OR WordArrays
		var kur = CryptoJS.lib.WordArray.create(new Uint8Array(fl_slice))
		// stuff the fucking WordArray down cryptoJS throat
		sha256.update(kur)
		// shift fot the next chunk read
		offs += chunk_size
	}
	// collapse shit into a hash
	return sha256.finalize().toString();
}




// the queue processor
// LFS starts from 70+ mb
// this is just the controller which returns controls
$this.upload_queue_ctrl = function()
{
	return {
		resume: function(){
			// if (this.alive == false){
			// 	print('cant launch because not alive already')
			// 	return
			// }
			if (this.alive == true){
				print('cant launch because alive already')
				return
			}
			this.alive = true
			$this.queue_iterator(this)
		},
		pause: function(){
			this.alive = false
		}
	}
}
$this.upload_queue = $this.upload_queue_ctrl()


// the actual queue iterator
$this.queue_iterator = async function(ctrl)
{
	// constantly try to grab the first element of the upload queue
	while(true){
		// if queue is empty - break
		if ($this.file_upload_q.length <= 0 || !ctrl.alive){break}
		// for now, always single threaded aka start processing the file from 0
		// even if it was marked as processing...
		const process_entry = $this.file_upload_q[0]
		
		// PROCESS FILE UPLOAD
		// FOR NOW ALWAYS LFS
		const lfs_done = await $this.lfs_upload(ctrl, process_entry)

		// once done uploading the file - delete it from the queue
		// assume some random shit and just do the following:
		if (lfs_done == true){
			$this.file_upload_q.shift()
		}
		print('fully done uploading shitty file')
	}
	print('done with the entire queue, abort may have been called')
	$this.upload_queue.pause()
}






// takes file and optional starting offset
$this.lfs_upload = async function(ctrl, inf, start_offs=0)
{
	const fl = inf['file']
	print('Calculating full hash...')
	const fl_hash = await $this.hash_file(fl)
	// BREAK POINT
	if(!ctrl.alive){return}
	print('Calculated full hash:', fl_hash)
	
	print('shit', inf['upl_token'], !inf['upl_token'])
	// try getting the upload token
	var lfs_upl_token = null
	if (!inf['upl_token']){
		const get_lfs_upl_token = await $all.core.py_get(
			'ft/upload',
			{
				'action': 'init_lfs',
				'declare_size': fl.size,
				'declare_hash': fl_hash,
				'file_name': fl.name,
				'dest_dir': inf['dest']
			},
			'json'
		)
		var lfs_upl_token = get_lfs_upl_token['token']
	}else{
		var lfs_upl_token = inf['upl_token']
	}
	inf['upl_token'] = lfs_upl_token

	// BREAK POINT
	if(!ctrl.alive){return}

	print('Asked to init lfs:', lfs_upl_token)


	// var offs = 0 + start_offs
	var offs = 0 + inf['live_shift']
	const chunk_size = (1024**2)*9

	// now that we have a token - iterate over the file
	while(true){
		// read slice as buffer
		var fl_chunk = await $this.read_file_slice(fl, [offs, offs+chunk_size])
		// BREAK POINT
		if(!ctrl.alive){return}


		// if slice is of 0 length it means that there's nothing left to send
		if (fl_chunk.byteLength <= 0){break}
		// otherwise - send it to the server
		var chunk_send_echo = await $all.core.py_send(
			'ft/upload',
			{
				'action': 'lfs_add',
				'upload_token': lfs_upl_token,
				'dest_dir': inf['dest']
			},
			fl_chunk,
			'text'
		)

		// shift file cursor
		offs += chunk_size
		inf['live_shift'] = offs
		print('Sent chunk to server:', chunk_send_echo)
		// BREAK POINT
		if(!ctrl.alive){return}
	}
	// BREAK POINT
	if(!ctrl.alive){return}

	// collapse LFS
	const collapse_response = await $all.core.py_get(
		'ft/upload',
		{
			'action': 'lfs_collapse',
			'upload_token': lfs_upl_token,
			'dest_dir': inf['dest']
		},
		'json'
	)
	// BREAK POINT
	if(!ctrl.alive){return}

	print('collapse response', collapse_response)

	return true

}