





$this.load_module = async function()
{
	await $all.core.sysloader('login');
}


$this.intrusion = async function()
{
	const try_login = await $all.core.py_cmd({
		'module': 'login/login',
		'rqt': 'get',
		'prms': {
			'action': 'login',
			'pswd': $('login #login_pswd').val().trim() || '0',
			'username': $('login #login_username').val().trim() || '0'
		},
		'load_as': 'json'
	})
	print(try_login)

	// if received token - reload
	if (try_login['jwt_token']){
		print(try_login)
		window.localStorage.setItem('auth_token', try_login['jwt_token'])
		window.location.reload()
	}else{
		$('login #login_box input').css('outline-color', 'red');
	}
}




$this.logout = function()
{
	window.localStorage.removeItem('auth_token');
	window.location.reload();
}
