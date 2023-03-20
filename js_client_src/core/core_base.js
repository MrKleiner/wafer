
// remappings
window.print = console.log;

const wafer_version = '$WAFER_VERSION_NUMBER$';

const obj_url = (window.URL || window.webkitURL);

const htbin = 'htbin';
const jwt_hname = 'wafer-jwt';

const _dev = true;
const _rawpy = false;

//
// Precache some icons
//
let _cache_request_data = _dev ? {
	headers: {
		'pragma': 'no-cache',
		'cache-control': 'no-cache',
	},
	cache: 'no-store'
} : {};

console.time('Icons cache')
const svg_icon_cache = {
	'warn_triangle' =   await (await fetch('/assets/icon_warn.svg', _cache_request_data)).text(),
	'err_cross' =       await (await fetch('/assets/icon_err.svg', _cache_request_data)).text(),
	'arrow_down' =      await (await fetch('/assets/arrow_down.svg', _cache_request_data)).text(),
	'spinning_circle' = await (await fetch('/assets/spinning_circle.svg', _cache_request_data)).text(),
}
console.time('Icons cache')



// mein kampf
window.mein_sleep = {}
const wfsleep =  async function(amt=500, ref='a') {
	return new Promise(function(resolve, reject){
		window.mein_sleep[ref] = setTimeout(function () {
			delete window.mein_sleep[ref]
			resolve(true)
		}, amt);
	});
}

function closest_num_from_array(arr, goal=0)
{
	return arr.reduce(function(prev, curr) {
		return (Math.abs(curr - goal) < Math.abs(prev - goal) ? curr : prev);
	});
}



//
// Fade out elements with help of css (rubbish)
//

class simple_fades
{
	constructor(amt=100, step=25) {
		// const amt = count;
		// const step = 1.0 / amt;
		// const step = step;
		this.name_base = window.crypto.getRandomValues(new BigUint64Array(1))[0].toString(36);

		this.fades = [];
		this.fades_rules = {};

		var fdur = 0;
		var css = `
			<style>

		`;
		for (var f = 0; f < amt; f++) {
			fdur += step;
			var record = (fdur / 1000).toFixed(3);
			this.fades_rules[fdur] = `wfade-${record.replace('.', '_')}`
			this.fades.push(fdur);
			css += `
				.wfade-${record.replace('.', '_')}
				{
					transition: ${(fdur / 1000).toFixed(3)}s !important;
					opacity: 0 !important;
				}
			`;
		}

		css += '</style>'

		$('body').append(css)

		// console.log(this.fades);
		// console.log(this.fades_rules);
	}

	closest_num_from_array(arr, goal=0){
		return arr.reduce(function(prev, curr) {
			return (Math.abs(curr - goal) < Math.abs(prev - goal) ? curr : prev);
		});
	}

	async sleep(amt=500) {
		return new Promise(function(resolve, reject){
			setTimeout(function () {
				resolve(true)
			}, amt);
		});
	}

	async fadeout(elem, duration=500){
		const tgt = $(elem);
		const entry = this.closest_num_from_array(this.fades, duration)
		$(elem).addClass(this.fades_rules[entry])
		await this.sleep(entry+5)
		tgt.remove()
	}

}
const fadesys = new simple_fades();


// type: warning / error,
// title: '',
// body: '',
// notice: '',
// life: 2000,
const gui_msg = async function(msg_info){
	const _defaults = {
		type: 'warning',
		title: '',
		body: null,
		notice: null,
		life: 2000,
	}
	const mconf = { ..._defaults, ...msg_info };
	const icon_dict = {
		'error': svg_icon_cache['err_cross'],
		'warning': svg_icon_cache['warn_triangle'],
	};
	const msg = $(`
		<div class="gui_msg ${mconf.type}">
			<div class="gui_msg_title">${icon_dict[mconf.type]} ${mconf.title}</div>
			<div class="gui_msg_body ${mconf.body ? '' : 'nodisplay'}">${mconf.body}</div>
			<div class="gui_msg_notice ${mconf.notice ? '' : 'nodisplay'}">${mconf.notice}</div>
		</div>
	`);

	$('#msg_pool').append(msg);
	await wfsleep(mconf.life);
	await fadesys.fadeout(msg, 500);
}

// convert file object to actual bytes/blob
const file_to_bytes = async function(file, doblob=false)
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









//
// Real shit
//


// todo this anon function is not needed. Isolate context with {}
const action_registry = {};

(function() {

	const _act_gateway_v0 = function(event, evt_type){
		const target_elem = event.target.closest('[wfact]');
		if (target_elem){
			const action = action_registry[target_elem.getAttribute('wfact')];
			if (!action){return}
			if (action.type == evt_type){
				// console.log(action_registry, action)
				action.exec(event, target_elem)
			}
		}
	}

	const _act_gateway = function(event, evt_type){
		const target_elem = event.target.closest('[wfact]');
		if (target_elem){
			const acts = target_elem.getAttribute('wfact').split(',');
			for (let act of acts){
				const action = action_registry[act];
				if (!action){continue}
				if (action.type == evt_type){
					// console.log(action_registry, action)
					action.exec(event, target_elem)
				}
			}
		}
	}

	const _listen_events = [
		'click',
		'input',
		'contextmenu',
		'keydown',
		// 'mousemove',
		'wheel',
	];

	for (let _binds of _listen_events){
		document.addEventListener(_binds, event => {
			_act_gateway(event, _binds)
		});
	}

})();

const register_action = function(name, atype, func){
	action_registry[name] = {
		'type': (`${atype}`).lower(),
		'exec': func,
	}
}






// load a specified system
// does nothing if no system specified
const sysloader = async function(panelname=null, as_return=false)
{
	// dont bother if invalid
	if (!panelname){
		print('Invalid system name:', panelname);
		return
	};

	const response = await fetch(`/html_panels/${panelname}.html`, {
		'headers': {
			'accept': '*/*',
			'cache-control': 'no-cache',
			'pragma': 'no-cache',
		},
		'method': 'GET',
		'mode': 'cors',
		'credentials': 'omit',
	})

	const panel_data = await response.text();

	if (as_return){
		return panel_data
	}

	document.querySelector('#pages_pool').innerHTML = data;
}




// method:         get/post
// prms:           a dictionary of query string parameters
// payload:        needed for post: A blob representing data to be sent to the server
// load_as:        treat response as text/json/buffer/blob
// return_query:   return a final request url string and don't do anything else. Default to false
// enable_cache:   whether to enable caching or not. Default is set to no cache at any circumstances
// omit_creds:     whether to omit credentials like cookies n shit. Default to false
const py_cmd = async function(pymodule=null, rprms=null)
{
	if (!pymodule || !rprms){
		console.error('py cmd: Insufficient params:', pymodule, rprms);
		return
	}

	// default headers
	const rq_headers = {
		'accept':        '*/*',
		'cache-control': 'no-cache',
		'pragma':        'no-cache',
	}
	// default config
	const pycmd_defaults = {
		// module is always autofilled now
		'module': '',

		'method':       'post',
		'prms':         {},
		'payload':      '',
		'load_as':      'text',
		'return_query': false,
		'enable_cache': false,
		'omit_creds':   false,
	}
	// overwrite default config with provided
	const config = { ...pycmd_defaults, ...rprms };

	// add jwt token to the headers list if it's present
	const jwt_token = window.localStorage.getItem('auth_token');
	if (jwt_token){
		rq_headers[jwt_hname] = add_jwt;
	}

	// split py file path and module action
	const mwa_split = pymodule.split('.');

	// specify action
	// todo: is this really a good way to handle actions ?
	// todo: is .at() slower than [1] ?
	config.prms['action'] = mwa_split.at(-1).trim();

	// convert params to URL params
	const urlParams = new URLSearchParams(config.prms);

	// construct the final request URL
	const tgt_url = `${htbin}/${mwa_split[0].trim()}.${_rawpy ? 'py' : 'pyc'}?${urlParams.toString()}`;

	// sometimes it's needed to return a final request url string and don't do anything else
	if (return_query){
		return tgt_url
	}

	// exec...
	return new Promise(async function(resolve, reject){
		const request_method = config.method.toLowerCase();

		const cache_condition = config.enable_cache ? 'default' : 'no-store'

		if (request_method == 'post'){
			// convert payload to BLOB
			const pl = new Blob([config.payload], {type: 'text/plain'});

			var response =
			await fetch(tgt_url, {
				'headers':     rq_headers,
				'method':      'POST',
				'body':        pl,
				'mode':        'cors',
				'credentials': 'include',
				'cache':       cache_condition,
			})
		}

		if (request_method == 'get'){
			var response =
			await fetch(tgt_url, {
				'headers':     rq_headers,
				'method':      'GET',
				'mode':        'cors',
				'credentials': 'include',
				'cache':        cache_condition,
			})
		}

		if (response.status == 404){
			console.warn(`py_cmd: server responded with 404 to a ${rqt} request`);
			return
		}

		// theoretically, with the new server system - no uncaught erros are possible...
		// so, before treating response body - check for errors
		if (response.headers.get('wafer-fatal-error') != null){
			const rtext = await response.text()
			console.error(`py_cmd: The response sez that a fatal error has occured on the server (${response.headers.get('wafer-fatal-error')}):`, rtext)
			gui_msg({
				type: 'error',
				title: `The server has reported a fatal error: ${response.headers.get('wafer-fatal-error')}`,
				body: rtext,
				notice: `If you're experiencing unexpected behaviour - please contact the system administrator`,
				life: 4000,
			})
			resolve(false)
			return
		}

		if (response.headers.get('wafer-error') != null){
			console.warn(`py_cmd: The server has included a warning in the response: ${response.headers.get('wafer-error')}`)
		}


		// no error means shit is formatted the expected way
		// well, really, the try/except block is just better...
		// actually, why not both ?

		// it's possible to only retreive one type of data from the response...
		// with no possibility of re-reading it...
		// just read as bytes right away
		// and then treat accordingly
		// const bin = new Uint8Array(await response.arrayBuffer())

		// update: no

		if (config.load_as == 'text'){
			// important todo: is there any difference between .text() and UTF8ArrToStr ?
			// resolve(lizard.UTF8ArrToStr(bin))
			resolve(await response.text())
			return
		}
		if (config.load_as == 'json'){
			// todo: why not use .json() ?
			// resolve(JSON.parse(lizard.UTF8ArrToStr(bin)))
			resolve(await response.json())
			return
		}
		if (config.load_as == 'buffer'){
			// resolve(bin)
			resolve(new Uint8Array(await response.arrayBuffer()))
			return
		}
		if (config.load_as == 'blob'){
			// todo: I SURE HOPE THAT THIS DOES NOT PERMANENTLY CACHE THIS BLOB IN ANY WAY
			resolve(await response.blob())
			return
		}
		console.warn(`py_cmd (${rqt}): falling back to default data type (text), because ${config.load_as} is an unknown type`);
		resolve(await response.text())
	});
}












