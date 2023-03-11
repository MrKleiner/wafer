



$this.browser_detection_shite = function()
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


$this.browser_detection = function()
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

	// NOBODY's going to use mobile!
	if (BrowserDetect.browser.lower() == 'safari' && !isMobile.any){
		$('body').html(`
			<div style="display: flex; font-size: 3.1vw; flex-direction: column; width: 100%; height: 100%; align-items: center; justify-content: center">
				<h1 style="color: red">Safari is NOT supported!! Use ANY other browser EXCEPT Safari!!!</h1>
				<img style="width: 100%; height: 50%; object-fit: contain; object-position: center;" src="../assets/safari_shit.webp">
			</div>
		`);
	}

}


// important todo: don't do this on every click...
$this.browser_detection_smart = function(evt)
{
	if (window.session_gotcha){return}

	// var winner = window.localStorage.getItem('browser_detected')

	const browser_detector = {

		// just so that it looks a little nicer
		exec: function(){
			// create the score board
			const haxtable = this.compat_table()

			// go through each entry
			var candidates = {
				'chrome': 0,
				'firefox': 0,
				'safari': 0
			}
			// test each system and score browsers
			for (let sys in haxtable){
				// https condition
				if (haxtable[sys].https == true && !window.isSecureContext){continue}

				var discovered = this.obj_walk(window, sys, !!haxtable[sys].last)
				// go trough every browser
				for (let browser in haxtable[sys]['browsers']){
					// check whether declared compat matches discovered
					// only collect mismatches
					candidates[browser] += (haxtable[sys]['browsers'][browser] != discovered) ? 1 : 0
				}
			}

			// store it, because why not
			this.scoreboard = candidates

			// flip keys and objects in the candidates dict
			var candidate_score = {}
			const c_keys = Object.keys(candidates)
			const c_vals = Object.values(candidates)
			for (let kp_index in c_keys){
				candidate_score[c_vals[kp_index]] = c_keys[kp_index]
			}

			// store it, because why not
			this.scoreboard_flipped = candidate_score

			// also store the winner
			const winner = candidate_score[Math.min(...Object.keys(candidate_score))]
			this.winner = winner
			return winner
		},

		// basically the main process
		compat_table: function(){
			const cp_table = {
				'chrome': {
					'yes': [
						window.isSecureContext ? !!window.FileSystemHandle : true,
						!!window.ImageCapture,
						window.isSecureContext ? !!window.navigator.locks.request : true,
						window.isSecureContext ? !!window.showOpenFilePicker : true,
						!!window.navigator.share,
						window.isSecureContext ? ((!!window.PushManager.prototype) ? !!window.PushManager.prototype.getSubscription : false) : true,
						!!window.URL,
						('outputLatency' in (new window.AudioContext)),
						('backdropFilter' in document.body.style),
						!!window.VideoFrame,
						!!window.VideoEncoder
					],
					'no': [
						!window.AudioContext.prototype.createMediaStreamTrackSource
					]
				},
				'firefox': {
					'yes': [
						!!window.AudioContext.prototype.createMediaStreamTrackSource,
						window.isSecureContext ? !!window.navigator.locks.request : true,
						window.isSecureContext ? ((!!window.PushManager.prototype) ? !!window.PushManager.prototype.getSubscription : false) : true,
						!!window.URL,
						('outputLatency' in (new window.AudioContext))
					],
					'no': [
						!window.FileSystemHandle,
						!window.ImageCapture,
						!window.navigator.share,
						!('backdropFilter' in document.body.style),
						!window.VideoFrame,
						!window.VideoEncoder,
						window.isSecureContext ? !window.showOpenFilePicker : true,
					]
				},
				'safari': {
					'yes': [
						!!window.FileSystemHandle,
						window.isSecureContext ? !!window.navigator.locks.request : true,
						window.isSecureContext ? ((!!window.PushManager.prototype) ? !!window.PushManager.prototype.getSubscription : false) : true,
						!!window.navigator.share
					],
					'no': [
						(window.FileSystemHandle) ? !window.FileSystemHandle.prototype.queryPermission : true,
						(window.FileSystemHandle) ? !window.FileSystemHandle.prototype.requestPermission : true,
						!window.ImageCapture,
						!window.AudioContext.prototype.createMediaStreamTrackSource,
						!('outputLatency' in (new window.AudioContext)),
						!('backdropFilter' in document.body.style),
						!window.VideoFrame,
						!window.VideoEncoder,
						window.isSecureContext ? !window.showOpenFilePicker : true,
					]
				}
			}

			const alt_table = {
				'FileSystemHandle': {
					'browsers': {
						'chrome': true,
						'firefox': false,
						'safari': true
					},
					'https': true
				},
				'ImageCapture': {
					'browsers': {
						'chrome': true,
						'firefox': false,
						'safari': false
					}
				},
				'navigator.locks.request': {
					'browsers': {
						'chrome': true,
						'firefox': true,
						'safari': true
					},
					'https': true
				},
				'showOpenFilePicker': {
					'browsers': {
						'chrome': true,
						'firefox': false,
						'safari': false
					},
					'https': true
				},
				'navigator.share': {
					'browsers': {
						'chrome': true,
						'firefox': false,
						'safari': true
					},
					'https': true
				},
				'PushManager.prototype.getSubscription': {
					'browsers': {
						'chrome': true,
						'firefox': true,
						'safari': true
					},
					'https': true
				},
				'AudioContext.prototype.outputLatency': {
					'browsers': {
						'chrome': true,
						'firefox': false,
						'safari': false
					},
					// last = should only be checked for presence and not execution
					'last': true
				},
				'AudioContext.prototype.createMediaStreamTrackSource': {
					'browsers': {
						'chrome': false,
						'firefox': true,
						'safari': false
					},
					// last = should only be checked for presence and not execution
					'last': true
				},
				'document.body.style.backdropFilter': {
					'browsers': {
						'chrome': true,
						'firefox': false,
						'safari': false
					}
				},
				'VideoFrame': {
					'browsers': {
						'chrome': true,
						'firefox': false,
						'safari': false
					}
				},
				'VideoEncoder': {
					'browsers': {
						'chrome': true,
						'firefox': false,
						'safari': false
					}
				},
				'FileSystemHandle.prototype.queryPermission': {
					'browsers': {
						'chrome': true,
						'firefox': false,
						'safari': false
					},
					'https': true
				},
				'FileSystemHandle.prototype.requestPermission': {
					'browsers': {
						'chrome': true,
						'firefox': false,
						'safari': false
					},
					'https': true
				},
				'FileSystemHandle.prototype.isSameEntry': {
					'browsers': {
						'chrome': true,
						'firefox': false,
						'safari': true
					},
					'https': true
				}
			}

			return alt_table
		},

		// walk object path
		obj_walk: function(ob, tgt, dolast=false, give_func=false){
			var current = ob
			const ob_path = tgt.split('.')
			for (let fpath of ob_path) {
				if (fpath in current){
					if (fpath == ob_path.at(-1) && dolast){break}
					current = current[fpath]
				}else{
					return false
				}
			}
		    return (give_func ? current : true)
		}
	}
	var winner = browser_detector.exec()

	// mobile
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

	if (winner == 'firefox'){
		document.body.setAttribute('shitfox', true)
	}
	// win a fuckoff
	if (winner == 'safari' && !isMobile.any()){
		$('body').html(`
			<div style="display: flex; font-size: 3.1vw; flex-direction: column; width: 100%; height: 100%; align-items: center; justify-content: center">
				<h1 style="color: red">Safari is NOT supported!! Use ANY other browser EXCEPT Safari!!!</h1>
				<img style="width: 100%; height: 50%; object-fit: contain; object-position: center;" src="../assets/safari_shit.webp">
			</div>
		`);
	}

	// window.localStorage.setItem('browser_detected', winner)

	window.session_gotcha = true;
}







