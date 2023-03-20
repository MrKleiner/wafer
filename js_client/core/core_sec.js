
if (!window.bootlegger){window.bootlegger = {}};

if (!window.bootlegger.core){window.bootlegger.core={}};





// remind outselves who we are
// this gets info like whether we're a guest, an admin, what kind of allowance do we have, etc...
async function whoami(){
	window.usr_info = await py_cmd('whoami', {
		'module':  'login/login',
		'rqt':     'get',
		'load_as': 'json',
	});

	// window.usr_info = _usr_info;
}







$(document).ready(async function(){
	// get current user info and store it in memory
	await whoami()
	// load an execute admin module if user is admin
	if (window.usr_info.isadmin){
		await import('/js_client/admin/admin.js')
	}
	await import('/js_client/auth/login.js')
});