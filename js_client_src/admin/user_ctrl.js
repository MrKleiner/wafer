const _example1 = {
	'isadmin': true,
	'edit_self': true,
	'server_render': true,
	'torrenting': false,
	'edit_thumbs': true,
	'recursive_nav': false,
	'userid': '1337',
	'login': 'Sex bomb',
	'pswd': 'lol',
	// 'shared_ruleset': 'shared_rule',
	'rules': {
		'global': [],
		'shared_rule': 'whatever',
		'apply_shared_after': false,
		'homedir': 'path/to/home',
		'target': [
			{
				'rule': 'path/relative/to/wafer/root1',
				'write': false,
				'recursive': false,
				'prohibit': false,
				'for_each': {
					'use': true,
					'deep': 2,
					'with_name': 'date'
				}
			},
			{
				'rule': 'path/relative/to/wafer/root2',
				'write': false,
				'recursive': false,
				'prohibit': false,
				'for_each': {
					'use': false,
					'deep': 2,
					'with_name': 'nen'
				}
			}
		]
	},
}

const _example2 = {
	'isadmin': false,
	'edit_self': false,
	'server_render': false,
	'torrenting': true,
	'recursive_nav': false,
	'edit_thumbs': true,
	'userid': '7979',
	'login': 'Door',
	'pswd': 'Hatch',
	// 'shared_ruleset': 'shared_rule',
	'rules': {
		'global': [],
		'shared_rule': 'another',
		'apply_shared_after': false,
		'homedir': 'path/to/home/sex',
		'target': [
			{
				'rule': 'path/relative/to/wafer/root1',
				'write': false,
				'recursive': false,
				'prohibit': false,
				'for_each': {
					'use': false,
					'deep': null,
					'with_name': null,
				}
			},
			{
				'rule': 'path/relative/to/wafer/root2',
				'write': false,
				'recursive': false,
				'prohibit': true,
				'for_each': {
					'use': false,
					'deep': null,
					'with_name': null,
				}
			}
		]
	},
}

// 
// parameter type definitions
// 
const base_params_types = {
	'login':   'input.text',
	'pswd':    'input.text',
	'homedir': 'input.text',
}
const perms_types = {
	'isadmin':       'bool',
	'edit_self':     'bool',
	'server_render': 'bool',
	'torrenting':    'bool',
	'edit_thumbs':   'bool',
	'recursive_nav': 'bool',
}
const rules_types = {
	'rule':      'input.text',
	'write':     'bool',
	'recursive': 'bool',
	'prohibit':  'bool',
	'use':       'bool',
	'deep':      'input.num',
	'with_name': 'input.text',
}


// 
// iterators
// 
const base_params_iter = {
	'login': 'Username:',
	'pswd':  'Password:',
}
const perms_iter = {
	'isadmin':       'Admin',
	'edit_self':     'Self Edit',
	'server_render': 'Server Render',
	'torrenting':    'Torrenting',
	'edit_thumbs':   'Edit Previews',
	'recursive_nav': 'Recursive Nav',
}
const rule_shared_iter = {
	'homedir': 'Homedir:',
}

const rule_base_iter = {
	'rule':      'Path:',
	'prohibit':  'Prohibit',
	'write':     'Write',
	'recursive': 'Recursive',
}

const rule_feach_iter = {
	'use':       'For Each',
	'deep':      'Depth',
	'with_name': 'With name:',
}



const params_html = {
	'input.text': function(label, paramname, val='none'){
		return $(`
			<div prm_name="${paramname}" class="usr_param_row">
				<div class="label">${label}</div>
				<input value="${val}" type="text">
			</div>
		`)
	},
	'input.num': function(label, paramname, val=0){
		return $(`
			<div prm_name="${paramname}" class="usr_param_row">
				<div class="label">${label}</div>
				<input value="${val}" type="number">
			</div>
		`)
	},
	'bool': function(label, paramname, val=false){
		return $(`
			<div prm_name="${paramname}" class="usr_param_row">
				<div class="label">${label}</div>
				<input ${val ? 'checked' : ''} type="checkbox">
			</div>
		`)
	},
}

const rip_types = {
	'input.text': function(elem){
		return $(elem).find('input')[0].value
	},
	'input.num': function(elem){
		return $(elem).find('input')[0].value
	},
	'bool': function(elem){
		return $(elem).find('input')[0].checked
	},
}




// a single user
class usr_ctrl
{
	constructor(_usr_info=null) {
		// adding new params:
		// 1 - Add to defaults
		// 2 - Add to type definition
		// 3 - Add to iterators
		// 4 - Add to creation
		this.modified = false;
		// marks this user for deletion
		this.deleted  = false;
		// whether it's a newly created user or not
		// this is flipped to true if _usr_info is left as null
		this.new      = false;

		const _defaults = {
			'isadmin':       false,
			'edit_self':     false,
			'server_render': false,
			'torrenting':    false,
			'edit_thumbs':   false,
			'recursive_nav': false,
			'userid':        null,
			'login':         'Sexbomb',
			'pswd':          'pwnt',
			// 'shared_ruleset': 'shared_rule',
			'rules': {
				'global':             [],
				'shared_rule':        null,
				'apply_shared_after': false,
				'homedir':            '/',
				'target':             [],
			},
		}

		if (_usr_info == null){
			this.new = true;
		}

		const usr_info = this.new ? _defaults : { ..._defaults, ..._usr_info };
		console.log('USER INFO', usr_info)

		this.userid = usr_info.userid;

		// create the base frame for all the other elements
		const usr_frame = $(`
			<div class="user">
				<div usrprm="login" class="username">${usr_info.login}</div>
				<div class="main_usr_params"></div>
				<div class="shared_ruleset usr_param_row">
					<div class="label">Shared ruleset:</div>
					<select></select>
				</div>
				<div class="global_ruleset"></div>
				<div class="user_perms"></div>
				<div class="tgt_rulesets">
					<div class="tgt_rulesets_title">Rules</div>
					<div class="tgt_rulesets_pool"></div>
				</div>
			</div>
		`);

		// store references to sections of the frame
		this.usr_elem = {
			root:           usr_frame,
			login_title:    usr_frame.find('.login'),
			main_prms:      usr_frame.find('.main_usr_params'),
			shared_ruleset: usr_frame.find('.shared_ruleset select'),
			permissions:    usr_frame.find('.user_perms'),
			rules_list:     usr_frame.find('.tgt_rulesets .tgt_rulesets_pool'),
		};

		// create base params
		for (let prm in base_params_iter){
			this.usr_elem.main_prms.append(
				params_html[base_params_types[prm]](base_params_iter[prm], prm, usr_info[prm])
			)
		}
		// shared rule params
		for (let prm in rule_shared_iter){
			this.usr_elem.main_prms.append(
				params_html[base_params_types[prm]](rule_shared_iter[prm], prm, usr_info.rules[prm])
			)
		}
		// permissions
		for (let prm in perms_iter){
			this.usr_elem.permissions.append(
				params_html[perms_types[prm]](perms_iter[prm], prm, usr_info[prm])
			)
		}

		// rules
		for (let rule of usr_info.rules.target){
			const rule_frame = $(`
				<rule ${rule.for_each.use ? 'for_enabled' : ''}></rule>
			`);

			// base params
			for (let rbase in rule_base_iter){
				rule_frame.append(
					params_html[rules_types[rbase]](rule_base_iter[rbase], rbase, rule[rbase])
				)
			}
			// for each params
			for (let feach in rule_feach_iter){
				rule_frame.append(
					params_html[rules_types[feach]](rule_feach_iter[feach], feach, rule.for_each[feach])
				)
			}
			this.usr_elem.rules_list.append(rule_frame)
		}

		// append rule to the pool
		$('#panel_root').append(usr_frame);
	}

	dump(){
		// console.log(this.usr_elem)

		const usr_info = {
			'rules': {
				'global': [],
				'target': [],
			}
		}

		// base params
		for (let prm in base_params_iter){
			const param_elem = this.usr_elem.main_prms.find(`[prm_name="${prm}"]`);
			// console.log(prm, param_elem, rip_types[base_params_types[prm]])
			usr_info[prm] = rip_types[base_params_types[prm]](param_elem)
		}
		// shared rule params
		for (let prm in rule_shared_iter){
			const param_elem = this.usr_elem.main_prms.find(`[prm_name="${prm}"]`);
			usr_info.rules[prm] = rip_types[base_params_types[prm]](param_elem)
		}
		// permissions
		for (let prm in perms_iter){
			const param_elem = this.usr_elem.permissions.find(`[prm_name="${prm}"]`);
			usr_info[prm] = rip_types[perms_types[prm]](param_elem)
		}

		// rules
		for (let rule of $(this.usr_elem.rules_list)[0].querySelectorAll('rule')){
			const rule_frame = {
				'for_each': {}
			}

			// base params
			for (let rule_param in rule_base_iter){
				const param_elem = $(rule).find(`[prm_name="${rule_param}"]`);
				rule_frame[rule_param] = rip_types[rules_types[rule_param]](param_elem)
			}
			// for each params
			for (let feach in rule_feach_iter){
				const param_elem = $(rule).find(`[prm_name="${feach}"]`);
				rule_frame.for_each[feach] = rip_types[rules_types[feach]](param_elem)
			}
			usr_info.rules.target.push(rule_frame)
		}

		return usr_info

	}

	kill(){
		this.deleted = true;
		this.modified = true;
		this.usr_elem.root.remove();
	}
}



const oof1 = new usr_ctrl(_example1)
const oof2 = new usr_ctrl(_example2)



console.log([oof1.dump(), oof2.dump()])


// $this.load = async function()


// load users
function load_user_list(){
	
}




