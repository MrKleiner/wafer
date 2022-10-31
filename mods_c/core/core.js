
if (!window.bootlegger){window.bootlegger = {}};

if (!window.bootlegger.core){window.bootlegger.core={}};

// remappings
window.print = console.log;

// important notes:
// preview indexing works as follows:
// a bunch of binaries (webp) where every name is sha256 of the path in the RAID pool

// dev temp
// window.localStorage.setItem('auth_token', '23849e61d01d323826345f22d6e0b3040d87b8c9d24ef7ad122ec805adac3590');



//
// presumable video preview / meta format:
//

// gigabin

// -----------------------------
// gigabin struct specification:
// -----------------------------

// First 7 bytes are strictly dedicated to the file format indication,
// aka first 7 bytes are a string "gigabin"

// Following 32 bytes are dedicated to the header size of the file in bytes
// any unused space out of these 32 bytes is padded with !

// Header is stored in the end of the entire file,
// allowing modification of the content without rewriting the entire file

// Header is a json encoded with Base64
// Header format:
// {
// 	'stores': {
// 		'filename': {
// 			'type': 'solid',
// 			'bits': [OFFSET_BYTES, LENGTH_BYTES, 'sha256 hash or null']
// 		},
// 		'filename2': [
// 			'type': 'array',
// 			'bits': [
// 				[OFFSET_BYTES, LENGTH_BYTES, 'sha256 hash or null'],
// 				[OFFSET_BYTES, LENGTH_BYTES, 'sha256 hash or null']
// 				...
// 			]
// 		]
// 	},
// 	'version': gigabin_version, like 0.7,
//	'total_size': 1 or null, (null by default)
// 	'comment': ''
// }

// sha256 is null by default in both libraries

// The rest of the file is a continous dump of bytes

// gigabin is available as a library for javascript and python
// The python version is the most efficient, since the entire fine doesn't has to be read


const obj_url = (window.URL || window.webkitURL);


//
// applicable formats
//

window.bootlegger.core.allowed_vid = [
	'mp4',
	'mov',
	'webm',
	'ts',
	'mts',
	'mkv',
	'avi'
]

window.bootlegger.core.allowed_img = [
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

window.bootlegger.core.allowed_img_special = [
	'tga',
	'psd',
	'arw',
	'raw',
	'hdr'
]














// load a specified system
// does nothing if no system specified
window.bootlegger.core.sysloader = async function(sysname=null, static=false)
{
	// dont bother if invalid
	if (!sysname){
		print('Invalid system name:', sysname);
	};

	// start loading...
	return new Promise(function(resolve, reject){
		fetch(`panels/${sysname}.html`, {
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
				print('Failed to load a panael', 'Reason:', 'File cannot be found on server');
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

window.bootlegger.core.browser_detection_shite = function()
{
	// Get the user-agent string
	let userAgentString = navigator.userAgent;

	// Detect Chrome
	let chromeAgent = userAgentString.indexOf('Chrome') > -1;

	// Detect Internet Explorer
	let IExplorerAgent = userAgentString.indexOf('MSIE') > -1 || userAgentString.indexOf('rv:') > -1;

	// Detect Firefox
	let firefoxAgent = userAgentString.indexOf('Firefox') > -1;

	// Detect Safari
	let safariAgent = userAgentString.indexOf('Safari') > -1;

	// Discard Safari since it also matches Chrome
	if ((chromeAgent) && (safariAgent)){
		safariAgent = false;
	}

	// Detect Opera
	let operaAgent = userAgentString.indexOf('OP') > -1;

	// Discard Chrome since it also matches Opera     
	if ((chromeAgent) && (operaAgent)){
		chromeAgent = false;
	}

	if (safariAgent){
		$('body').html(`
			<div style="display: flex; width: 100%; height: 100%; align-items: center; justify-content: center">
				<h1 style="color: white">Safari is NOT supported!! Use ANY other browser EXCEPT Safari!!!<h1>
				<img style="width: 100%; height: 50%; object-fit: contain; object-position: center;" src="./assets/fuck_safari.webp">
			</div>
		`);
	}

}


window.bootlegger.core.browser_detection = function()
{
	// browser detect
	var BrowserDetect = {
	        init: function(userAgent, appVersion) {
			this.browser = this.searchString(this.dataBrowser) || "An unknown browser";
			this.version = this.searchVersion(userAgent) || this.searchVersion(appVersion) || "an unknown version";
			this.OS = this.searchString(this.dataOS) || "an unknown OS";
		},
		searchString: function(data) {
			for (var i = 0; i < data.length; i++) {
				var dataString = data[i].string;
				var dataProp = data[i].prop;
				this.versionSearchString = data[i].versionSearch || data[i].identity;
				if (dataString) {
	              if (dataString.indexOf(data[i].subString) != -1) {
	                return data[i].identity;
	              }
				} else if (dataProp) {
	              return data[i].identity;
	            }
			}
		},
		searchVersion: function(dataString) {
			var index = dataString.indexOf(this.versionSearchString);
			if (index == -1) return;
			return parseFloat(dataString.substring(index + this.versionSearchString.length + 1));
		},
		dataBrowser: [{
			string: navigator.userAgent,
			subString: "Chrome",
			identity: "Chrome"
		}, {
			string: navigator.userAgent,
			subString: "OmniWeb",
			versionSearch: "OmniWeb/",
			identity: "OmniWeb"
		}, {
			string: navigator.vendor,
			subString: "Apple",
			identity: "Safari",
			versionSearch: "Version"
		}, {
			prop: window.opera,
			identity: "Opera",
			versionSearch: "Version"
		}, {
			string: navigator.vendor,
			subString: "iCab",
			identity: "iCab"
		}, {
			string: navigator.vendor,
			subString: "KDE",
			identity: "Konqueror"
		}, {
			string: navigator.userAgent,
			subString: "Firefox",
			identity: "Firefox"
		}, {
			string: navigator.vendor,
			subString: "Camino",
			identity: "Camino"
		}, { // for newer Netscapes (6+)
			string: navigator.userAgent,
			subString: "Netscape",
			identity: "Netscape"
		}, {
			string: navigator.userAgent,
			subString: "MSIE",
			identity: "Explorer",
			versionSearch: "MSIE"
		}, {
	        string: navigator.userAgent,
	        subString: "Trident",
			identity: "Explorer",
			versionSearch: "rv"
	     }, {
	        string: navigator.userAgent,
			subString: "Edge",
			identity: "Edge"
		}, {
			string: navigator.userAgent,
			subString: "Gecko",
			identity: "Mozilla",
			versionSearch: "rv"
		}, { // for older Netscapes (4-)
			string: navigator.userAgent,
			subString: "Mozilla",
			identity: "Netscape",
			versionSearch: "Mozilla"
		}],
		dataOS: [{
			string: navigator.platform,
			subString: "Win",
			identity: "Windows"
		}, {
			string: navigator.platform,
			subString: "Mac",
			identity: "Mac"
		}, {
			string: navigator.userAgent,
			subString: "iPhone",
			identity: "iPhone/iPod"
		}, {
			string: navigator.platform,
			subString: "Linux",
			identity: "Linux"
		}]

	};
	BrowserDetect.init(navigator.userAgent, navigator.appVersion);

	///// mobile
	var isMobile = {
	    Android: function() {
	        return navigator.userAgent.match(/Android/i);
	    },
	    BlackBerry: function() {
	        return navigator.userAgent.match(/BlackBerry/i);
	    },
	    iOS: function() {
	        return navigator.userAgent.match(/iPhone|iPad|iPod/i);
	    },
	    Opera: function() {
	        return navigator.userAgent.match(/Opera Mini/i);
	    },
	    Windows: function() {
	        return navigator.userAgent.match(/IEMobile/i);
	    },
	    any: function() {
	        return (isMobile.Android() || isMobile.BlackBerry() || isMobile.iOS() || isMobile.Opera() || isMobile.Windows());
	    }
	};

	window.user_browser = BrowserDetect

	if (BrowserDetect.browser.lower() == 'safari'){
		$('body').html(`
			<div style="display: flex; font-size: 3.1vw; flex-direction: column; width: 100%; height: 100%; align-items: center; justify-content: center">
				<h1 style="color: red">Safari is NOT supported!! Use ANY other browser EXCEPT Safari!!!</h1>
				<img style="width: 100%; height: 50%; object-fit: contain; object-position: center;" src="../assets/safari_shit.webp">
			</div>
		`);
	}

}


$(document).ready(function(){
	window.bootlegger.core.browser_detection()
	window.bootlegger.main_pool.module_loader();
	window.bootlegger.core.profiler();
	// wtf_kill_js();
});


// prms: URL parameters to pass to the CGI script
// as: treat response as text/json/buffer
// returns json with response status and payload
window.bootlegger.core.py_get = async function(mod='', prms={}, load_as='text')
{
	print('Exec PY get')

	// add auth token to the request
	prms['auth'] = window.localStorage.getItem('auth_token') || 'ftp';

	// convert payload to URL params
	const urlParams = new URLSearchParams(prms);

	// exec...
	return new Promise(function(resolve, reject){
		fetch(`htbin/${mod}.py?${urlParams.toString()}`, {
			'headers': {
				'accept': '*/*',
				'cache-control': 'no-cache',
				'pragma': 'no-cache'
			},
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
window.bootlegger.core.py_send = async function(mod='', prms={}, payload='', load_as='text')
{
	// add auth token to the payload
	prms['auth'] = window.localStorage.getItem('auth_token') || 'ftp';

	// convert params to URL params
	const urlParams = new URLSearchParams(prms);

	// convert payload to BLOB
	const pl = new Blob([payload], {type: 'text/plain'});

	// exec...
	return new Promise(function(resolve, reject){
		fetch(`htbin/${mod}.py?${urlParams.toString()}`, {
			'headers': {
				'accept': '*/*',
				'cache-control': 'no-cache',
				'pragma': 'no-cache'
			},
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
window.bootlegger.core.profiler = function()
{
	if (window.localStorage.getItem('auth_token')){
		$('body').attr('logged_in', true)
	}
}



window.bootlegger.core.load_dbfile = function(flpath, load_as)
{
	return new Promise(function(resolve, reject){
		fetch(`db/${flpath.strip('/')}`, {
			'headers': {
				'accept': '*/*',
				'cache-control': 'no-cache',
				'pragma': 'no-cache'
			},
			'method': 'GET',
			'mode': 'cors',
			'credentials': 'omit'
		})
		.then(async function(response) {
			// console.log(response.status);
			if (response.status == 404){
				resolve('DB File load: File does not exist')
				return
			}

			// todo: Just use response[GET AS]
			// and require this function to take proper read as statements

			// TEXT
			if (load_as == 'text'){
				resolve(await response.text())
				return
			}

			// JSON
			if (load_as == 'json'){
				resolve(await response.json())
				return
			}

			// buffer
			if (load_as == 'buffer'){
				resolve(await response.arrayBuffer())
				return
			}

			resolve(await response.text())
			return


		});
	});
}



window.bootlegger.core.file_to_bytes = async function(file, doblob=false)
{
	return new Promise(function(resolve, reject){
		var reader = new FileReader();
	    reader.readAsArrayBuffer(file, 'UTF-8');
	    reader.onload = function (evt) {
	    	// convert read result to blob
	    	if (doblob == true){
	    		var boobs = new Blob([reader.result], {type: file.type});
	    		resolve(boobs)
	    		return
	    	}else{
	    		resolve(reader.result)
	    	}
		};
	});
}


async function wtf_kill_js()
{
	window.bootlegger.core.fsys_root = (await window.bootlegger.core.load_dbfile('root.json', 'json'))['root_path'];
}



window.bootlegger.core.display_help = function()
{
	$('#help_overlay').toggleClass('hidden');
}
