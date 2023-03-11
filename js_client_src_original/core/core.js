
// remappings
window.print = console.log;


// dev temp
// window.localStorage.setItem('auth_token', '23849e61d01d323826345f22d6e0b3040d87b8c9d24ef7ad122ec805adac3590');

const wafer_version = '$WAFER_VERSION_NUMBER$';

const obj_url = (window.URL || window.webkitURL);

const htbin = 'htbin';



// important todo: https://stackoverflow.com/questions/16090530/how-to-point-a-websocket-to-the-current-server

//
// applicable formats
//

// important todo: this has to be requested from server on load

$this.allowed_vid = [
	'mp4',
	'mov',
	'webm',
	'ts',
	'mts',
	'mkv',
	'avi'
]

$this.allowed_img = [
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
	'hdr'
]

$this.allowed_img_special = [
	'tga',
	'psd',
	'arw',
	'raw',
	'hdr'
]


function closest_num_from_array(arr, goal=0)
{
	return arr.reduce(function(prev, curr) {
		return (Math.abs(curr - goal) < Math.abs(prev - goal) ? curr : prev);
	});
}
















































// load a specified system
// does nothing if no system specified
$this.sysloader = async function(sysname=null, static=false)
{
	// dont bother if invalid
	if (!sysname){
		print('Invalid system name:', sysname);
	};

	// start loading...
	return new Promise(async function(resolve, reject){
		fetch(`html_panels/${sysname}.html`, {
			'headers': {
				'accept': '*/*',
				'cache-control': 'no-cache',
				'pragma': 'no-cache'
			},
			'method': 'GET',
			'mode': 'cors',
			'credentials': 'omit'
		})
		.then(function(response) {
			// print(response.status);
			if (response.status == 404){
				print('Failed to load a panel', 'Reason:', 'File cannot be found on server');
				resolve({'ok': false, 'reason': 'invalid_url'})
				return
			}
			response.text().then(function(data) {
				print('Found requested panel on server, loading...', sysname, data)
				window.current_sys = sysname;
				document.querySelector('#pages_pool').innerHTML = data;
				if (static == true){
					document.querySelector('html').setAttribute('static', true);
				}else{
					document.querySelector('html').removeAttribute('static');
				}
				resolve(true)
			});
		});
	});
}






// prms: URL parameters to pass to the CGI script
// as: treat response as text/json/buffer
// returns json with response status and payload
$this.py_gets = async function(mod='', prms={}, load_as='text')
{
	print('Exec PY get')

	const rq_headers = {
		'accept': '*/*',
		'cache-control': 'no-cache',
		'pragma': 'no-cache'
	}

	const add_jwt = window.localStorage.getItem('auth_token')
	if (add_jwt){
		rq_headers['jwt'] = add_jwt
	}

	// convert payload to URL params
	const urlParams = new URLSearchParams(prms);

	// exec...
	return new Promise(function(resolve, reject){
		fetch(`${htbin}/${mod}.pyc?${urlParams.toString()}`, {
			'headers': rq_headers,
			'method': 'GET',
			'mode': 'cors',
			'credentials': 'omit'
		})
		.then(async function(response) {
			// print(response.status);
			if (response.status == 404){
				print('Failed to execute py get request');
				return
			}

			// honestly, FUCKOFF
			// this is just fine
			const bin = new Uint8Array(await response.arrayBuffer())

			// todo: for now use try catch
			// come up with something adequate later....
			try {
				if (load_as == 'text'){
					resolve(lizard.UTF8ArrToStr(bin))
					return
				}
				if (load_as == 'json'){
					resolve(JSON.parse(lizard.UTF8ArrToStr(bin)))
					return
				}
				if (load_as == 'buffer'){
					resolve(bin)
					return
				}
				if (load_as == 'blob'){
					const boobs = new Blob([bin], {});
					resolve(boobs)
					return
				}
				if (load_as == 'blob_url'){
					const boobs = new Blob([bin], {});
					resolve(obj_url.createObjectURL(boobs))
					return
				}
				console.warn('PyGet Warn: falling back to default data type');
				resolve(lizard.UTF8ArrToStr(bin))

			} catch (error) {
				console.warn('PyGet Error', lizard.UTF8ArrToStr(bin))
			}

		});
	});
}



// prms: URL parameters to pass to the CGI script
// payload: payload to send. Has to be proper shit and not raw objects
// as: treat response as text/json/buffer
$this.py_sends = async function(mod='', prms={}, payload='', load_as='text')
{
	const rq_headers = {
		'accept': '*/*',
		'cache-control': 'no-cache',
		'pragma': 'no-cache'
	}

	const add_jwt = window.localStorage.getItem('auth_token')
	if (add_jwt){
		rq_headers['jwt'] = add_jwt
	}
	
	// prms['auth'] = window.localStorage.getItem('auth_token') || 'ftp';

	// convert params to URL params
	const urlParams = new URLSearchParams(prms);

	// convert payload to BLOB
	const pl = new Blob([payload], {type: 'text/plain'});

	// exec...
	return new Promise(function(resolve, reject){
		fetch(`${htbin}/${mod}.pyc?${urlParams.toString()}`, {
			'headers': rq_headers,
			'method': 'POST',
			'body': pl,
			'mode': 'cors',
			'credentials': 'omit'
		})
		.then(async function(response) {
			// print(response.status);
			if (response.status == 404){
				print('Failed to execute py SEND request');
				return
			}

			// honestly, FUCKOFF
			// this is just fine
			const bin = new Uint8Array(await response.arrayBuffer())

			// todo: for now use try catch
			// come up with something adequate later....
			try {
				if (load_as == 'text'){
					resolve(lizard.UTF8ArrToStr(bin))
					return
				}
				if (load_as == 'json'){
					resolve(JSON.parse(lizard.UTF8ArrToStr(bin)))
					return
				}
				if (load_as == 'buffer'){
					resolve(bin)
					return
				}
				console.warn('PySend Warn: falling back to default data type');
				resolve(lizard.UTF8ArrToStr(bin))

			} catch (error) {
				console.warn('PySend Error', lizard.UTF8ArrToStr(bin), error)
			}

		});
	});
}







// determine whether the user is logged in or not
$this.profiler = function()
{
	if (window.localStorage.getItem('auth_token')){
		$('body').attr('logged_in', true)
	}
}



$this.file_to_bytes = async function(file, doblob=false)
{
	return new Promise(function(resolve, reject){
		var reader = new FileReader();
	    reader.readAsArrayBuffer(file, 'UTF-8');
	    reader.onload = function (evt) {
	    	// convert read result to blob
	    	if (doblob == true){
	    		const boobs = new Blob([reader.result], {type: file.type});
	    		resolve(boobs)
	    		return
	    	}else{
	    		resolve(reader.result)
	    	}
		};
	});
}




$this.display_help = function()
{
	$('#help_overlay').toggleClass('hidden');
}













