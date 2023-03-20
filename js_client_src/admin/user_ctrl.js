const _example1 = {
	'isadmin': true,
	'edit_self': true,
	'server_render': true,
	'torrenting': false,
	'edit_thumbs': true,
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

// a single user
class usr_ctrl
{
	constructor(usr_info={}) {
		this.modified = false;
		this.deleted = false;
		this.userid = usr_info.userid;

		this.usr_elem = $(`
			<div class="user">
				<div class="username">${usr_info.login}</div>

				<div class="username_input">
					<div class="label">Username:</div>
					<input value="${usr_info.login}" type="text">
				</div>
				<div class="password">
					<div class="label">Password:</div>
					<input value="${usr_info.pswd}" type="text">
				</div>
				<div class="homedir">
					<div class="label">Homedir:</div>
					<input value="${usr_info.rules.homedir}" type="text">
				</div>

				<div class="shared_ruleset">
					<div class="label">Shared ruleset:</div>
					<select>
					</select>
				</div>
				<div class="global_ruleset"></div>
				<div class="user_perms">
					<div prm="isadmin" class="user_perm_row">
						<div class="user_perm_row_label">Admin</div>
						<input ${usr_info.isadmin ? 'checked' : ''} type="checkbox">
					</div>
					<div prm="edit_self" class="user_perm_row">
						<div class="user_perm_row_label">Self Edit</div>
						<input ${usr_info.edit_self ? 'checked' : ''} type="checkbox">
					</div>
					<div prm="server_render" class="user_perm_row">
						<div class="user_perm_row_label">Server Render</div>
						<input ${usr_info.server_render ? 'checked' : ''} type="checkbox">
					</div>
					<div prm="torrenting" class="user_perm_row">
						<div class="user_perm_row_label">Torrenting</div>
						<input ${usr_info.torrenting ? 'checked' : ''} type="checkbox">
					</div>
					<div prm="edit_thumbs" class="user_perm_row">
						<div class="user_perm_row_label">Edit Previews</div>
						<input ${usr_info.edit_thumbs ? 'checked' : ''} type="checkbox">
					</div>
				</div>
				<div class="tgt_rulesets">
					<div class="tgt_rulesets_title">Rules</div>
					<div class="tgt_rulesets_pool"></div>
				</div>
			</div>
		`);
		
		this.rule_pool = this.usr_elem.find('.tgt_rulesets .tgt_rulesets_pool');
		this.shared_rule_sel = this.usr_elem.find('.shared_ruleset select')[0];
		
		// spawn regular rules
		for (let usr_rule of usr_info.rules.target){
			this.rule_pool.append(`
				<rule ${usr_rule.for_each.use ? 'for_enabled' : ''}>
						<rule-path>
							<wflabel>Path:</wflabel>
							<input value="${usr_rule.rule}" type="text">
						</rule-path>
						<rule-perms>
							<prohibit class="rule_perm">
								<wflabel>Prohibit</wflabel>
								<input ${usr_rule.prohibit ? 'checked' : ''} type="checkbox">
							</prohibit>
							<can-write class="rule_perm">
								<wflabel>Write</wflabel>
								<input ${usr_rule.write ? 'checked' : ''} type="checkbox">
							</can-write>
							<recursive class="rule_perm">
								<wflabel>Recursive</wflabel>
								<input ${usr_rule.recursive ? 'checked' : ''} type="checkbox">
							</recursive>
							<for-each class="rule_perm">
								<wflabel>For Each:</wflabel>
								<input ${usr_rule.for_each.use ? 'checked' : ''} type="checkbox">
							</for-each>
							<depth class="rule_perm">
								<wflabel>Depth:</wflabel>
								<input value="${usr_rule.for_each.deep || '0'}" type="number">
							</depth>
							<with-name class="rule_perm">
								<wflabel>With Name:</wflabel>
								<input value="${usr_rule.for_each.with_name || ''}" type="text">
							</with-name>
						</rule-perms>
					</rule>
			`);
		}
		
		// Do not populate shared ruleset, because it's later evaluated on each expand
		if (usr_info.rules.shared_rule){
			this.shared_rule_sel.add($(`<option value="${usr_info.rules.shared_rule}">${usr_info.rules.shared_rule}</option>`)[0]);
			this.shared_rule_sel.value = usr_info.rules.shared_rule;
		}

		// append rule to the pool
		$('#panel_root').append(this.usr_elem)
	}

	dump(){
		// console.log(this.usr_elem)
		var usr_info = {
			'isadmin':        this.usr_elem.find('.user_perms [prm="isadmin"] input')[0].checked,
			'edit_self':      this.usr_elem.find('.user_perms [prm="edit_self"] input')[0].checked,
			'server_render':  this.usr_elem.find('.user_perms [prm="server_render"] input')[0].checked,
			'torrenting':     this.usr_elem.find('.user_perms [prm="torrenting"] input')[0].checked,
			'edit_thumbs':    this.usr_elem.find('.user_perms [prm="edit_thumbs"] input')[0].checked,
			'userid':         this.userid,
			'login':          this.usr_elem.find('.username_input input').val().trim(),
			'pswd':           this.usr_elem.find('.password input').val().trim(),
			// 'shared_ruleset': this.usr_elem.find('.shared_ruleset select')[0].value,
			'rules': {
				'global': [],
				'shared_rule':        this.usr_elem.find('.shared_ruleset select')[0].value,
				'apply_shared_after': false,
				'homedir':            this.usr_elem.find('.homedir input').val().trim(),
				'target': [],
			},
		};

		for (let _tgtr of this.usr_elem[0].querySelectorAll('.tgt_rulesets .tgt_rulesets_pool rule')){
			const tgtr = $(_tgtr);
			usr_info.rules.target.push({
				'rule':         tgtr.find('rule-path input').val().trim(),
				'prohibit':     tgtr.find('rule-perms prohibit input')[0].checked,
				'write':        tgtr.find('rule-perms can-write input')[0].checked,
				'recursive':    tgtr.find('rule-perms recursive input')[0].checked,
				'for_each': {
					'use':       tgtr.find('rule-perms for-each input')[0].checked,
					'deep':      parseInt(tgtr.find('rule-perms depth input')[0].value),
					'with_name': tgtr.find('rule-perms with-name input')[0].value,
				}
			})
		}

		return usr_info

	}

	kill(){
		this.deleted = true;
		this.modified = true;
		this.usr_elem.remove();
	}
}



// const oof1 = new usr_ctrl(_example1)
// const oof2 = new usr_ctrl(_example2)



// console.log([oof1.dump(), oof2.dump()])


// $this.load = async function()


// load users
function load_user_list(){
	
}




