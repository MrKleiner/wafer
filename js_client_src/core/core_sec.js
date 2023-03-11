




// remind outselves who we are
// this gets info like whether we're a guest, an admin, what kind of allowance do we have, etc...
async function whoami(){
	const _usr_info = await py_cmd({
		'module':  'login/login',
		'rqt':     'get',
		'load_as': 'json',
	});

	window.usr_info = _usr_info;
}







$(document).ready(async function(){
	// get current user info and store it in memory
	await whoami()
	// load an execute admin module if user is admin
	if (window.usr_info.isadmin){
		await import('/admin.js')
	}
});