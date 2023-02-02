

document.addEventListener('change', tr_event => {
	validate()
});


async function validate(){
	$('#execute_setup').addClass('exec_locked')
	$('main .param_row').removeClass('row_ok row_ded')
	$('main .param_row .err').text('')
	$('main .param_row .warn').text('')
	const collected = {};
	const collision = []
	for (let prmr of document.querySelectorAll('main .param_row')){
		// console.log(prmr.id)
		inp = $(prmr).find('input')
		inp_val = inp.val().trim()
		if (inp_val != ''){
			collected[prmr.id] = inp_val
			if (collision.includes(inp_val)){
				$('main .param_row .err').text('Collision in file paths/port numbers detected (this means there are two identical paths/ports somewhere)')
				return
			}
			collision.push(inp_val)
		}
	}

	const pl = new Blob([JSON.stringify(collected)], {type: 'text/plain'});
	const response = await fetch('./validate.py', {
		'method': 'POST',
		'body': pl,
		'mode': 'cors',
		'credentials': 'omit'
	})
	const decision = await response.json()

	console.log(decision)

	const entries = decision[1]

	for (let prmr of document.querySelectorAll('main .param_row')){
		if (prmr.id in entries && entries[prmr.id] != true){
			$(prmr).addClass('row_ded')
			$(prmr).find('.err').text(entries[prmr.id])
		}
		if (prmr.id in entries && entries[prmr.id] == true){
			$(prmr).addClass('row_ok')
		}
	}

	if (decision[0] == true){
		$('#execute_setup').removeClass('exec_locked')
		window.wafer_data = pl
	}
}


async function exec_setup()
{
	const response = await fetch('./server_setup.py', {
		'method': 'POST',
		'body': window.wafer_data,
		'mode': 'cors',
		'credentials': 'omit'
	})
	const decision = await response.text()

	print(decision)
}











