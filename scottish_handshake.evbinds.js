document.addEventListener('click', tr_event => {


	// ==========================================
	// 	home home
	// ==========================================

	if (event.target.closest('#app_topbar #nav_login')){window.bootlegger.login.load_module()}
	if (event.target.closest('#app_topbar #nav_sign_out')){window.bootlegger.login.logout()}
	if (event.target.closest('#app_topbar #nav_enter_edit')){window.bootlegger.admin.load_module()}
	if (event.target.closest('#app_topbar #nav_go_home')){window.bootlegger.main_pool.home_button()}
	if (event.target.closest('#app_topbar #nav_display_help, #help_overlay')){window.bootlegger.core.display_help()}
	if (event.target.closest('lzdropdown .lz_menu_entries [dropdown_set]')){lzdrops.set_active(event.target.closest('lzdropdown .lz_menu_entries [dropdown_set]'))}
	if (event.target.closest('[haslizdropdown], lzdropdown')){lzdrops.showhide(event.target.closest('[haslizdropdown], lzdropdown'))}else{lzdrops.showhide(event.target.closest('[haslizdropdown], lzdropdown'))}




	// ==========================================
	// 	admin admin
	// ==========================================

	if (event.target.closest('admin btn#save_users')){window.bootlegger.admin.save_user_profiles()}
	if (event.target.closest('admin btn#spawn_new_user')){window.bootlegger.admin.add_user_profile()}
	if (event.target.closest('admin .usr_profile .userlist_kill_user')){window.bootlegger.admin.userlist_kill_user(event.target.closest('admin .usr_profile .userlist_kill_user'))}
	if (event.target.closest('admin .alw_list_folders .alw_kill_folder')){window.bootlegger.admin.alw_kill_folder(event.target.closest('admin .alw_list_folders .alw_kill_folder'))}
	if (event.target.closest('admin .alw_list_folders .alw_kill_admin')){window.bootlegger.admin.alw_kill_admin(event.target.closest('admin .alw_list_folders .alw_kill_admin'))}
	if (event.target.closest('admin .alw_add_folder')){window.bootlegger.admin.add_allowed_folder(event.target.closest('admin .alw_add_folder'))}
	if (event.target.closest('admin .alw_add_admin')){window.bootlegger.admin.add_admin_allowance(event.target.closest('admin .alw_add_admin'))}
	if (event.target.closest('admin #save_access_list')){window.bootlegger.admin.save_allowance_list()}
	if (event.target.closest('admin f-comp #commands lzdropdown [dropdown_set]')){window.bootlegger.admin.eval_match_name_hint()}
	if (event.target.closest('admin f-comp #spawn_match_struct')){window.bootlegger.admin.spawn_match_struct()}




	// ==========================================
	// 	login login
	// ==========================================

	if (event.target.closest('login #intrusion')){window.bootlegger.login.intrusion()}




	// ==========================================
	// 	main_pool main_pool
	// ==========================================

	if (event.target.closest('mpool flist flist-entry.league')){window.bootlegger.main_pool.list_league_matches(event.target.closest('mpool flist flist-entry.league'))}
	if (event.target.closest('mpool flist flist-entry.match')){window.bootlegger.main_pool.list_match_struct(event.target.closest('mpool flist flist-entry.match'))}
	if (event.target.closest('mpool flist flist-entry.struct_entry')){window.bootlegger.main_pool.list_media(event.target.closest('mpool flist flist-entry.struct_entry'))}
	if (event.target.closest('mpool[grid] flist flist-entry.media_entry:not(.lfs_entry) etype, mpool[list] flist flist-entry.media_entry:not(.lfs_entry)')){window.bootlegger.main_pool.load_fullres_media(event.target.closest('mpool[grid] flist flist-entry.media_entry:not(.lfs_entry) etype, mpool[list] flist flist-entry.media_entry:not(.lfs_entry)'))}
	if (event.target.closest('img#pic_fullres_preview')){window.bootlegger.main_pool.viewing_fullres = false;$('img#pic_fullres_preview').remove()}
	if (event.target.closest('mpool #exec_dlq_download')){window.bootlegger.ft.dl_many()}
	if (event.target.closest('mpool #select_all_items')){window.bootlegger.main_pool.select_all_in_folder()}
	if (event.target.closest('mpool')){$('flist-entry').removeClass('arrow_cycle_hint')}
	if (event.target.closest('#mpool_tobpar #vispath .vispath_fld')){window.bootlegger.main_pool.vispath_clicker(event.target.closest('#mpool_tobpar #vispath .vispath_fld'))}
	if (event.target.closest('flist-entry.mde_vid')){window.bootlegger.main_pool.open_webm_preview(event.target.closest('flist-entry.mde_vid'))}
	if (event.target.closest('#webm_preview #webm_video_waveform')){window.bootlegger.main_pool.nav_webm_audio(tr_event, event.target.closest('#webm_preview #webm_video_waveform'))}
	if (event.target.closest('#webm_preview #timeline_ctrl #tl_stop')){window.bootlegger.main_pool.pause_webm()}
	if (event.target.closest('#webm_preview #timeline_ctrl #tl_play')){window.bootlegger.main_pool.play_webm()}




	// ==========================================
	// 	sys_chooser syschoser
	// ==========================================

	if (event.target.closest('syschoose #sysc_vids')){window.bootlegger.vidman.load_module()}




	// ==========================================
	// 	vidman vidman
	// ==========================================

	if (event.target.closest('vman_admin #vma_add_pool_src')){window.bootlegger.vidman.add_src_pool_entry()}
	if (event.target.closest('vman_admin .srcs_pool_entry img')){window.bootlegger.vidman.del_src_pool_entry(event.target.closest('vman_admin .srcs_pool_entry img'))}
	if (event.target.closest('vman_admin #vma_save_sources')){window.bootlegger.vidman.save_vid_pool_srcs()}
	if (event.target.closest('#tree_pool_entries .entry_folder')){window.bootlegger.vidman.list_vids(event.target.closest('#tree_pool_entries .entry_folder'))}


});


document.addEventListener('input', tr_event => {


	// ==========================================
	// 	admin admin
	// ==========================================

	if (event.target.closest('admin #userlist .usr_profile input.profile_login')){window.bootlegger.admin.validate_users_nicknames(event.target.closest('admin #userlist .usr_profile input.profile_login'))}
	if (event.target.closest('admin f-comp #plus_days')){window.bootlegger.admin.eval_match_name_hint()}


});


document.addEventListener('contextmenu', tr_event => {


	// ==========================================
	// 	admin admin
	// ==========================================

	if (event.target.closest('admin #folder_maker #foldmaker_pool > .team')){window.bootlegger.admin.select_team_folder(tr_event, event.target.closest('admin #folder_maker #foldmaker_pool > .team'))}




	// ==========================================
	// 	main_pool main_pool
	// ==========================================

	if (event.target.closest('flist-entry.media_entry:not(.lfs_entry)')){window.bootlegger.main_pool.add_media_entry_to_selection(tr_event, event.target.closest('flist-entry.media_entry:not(.lfs_entry)'))}
	if (event.target.closest('img#pic_fullres_preview')){window.bootlegger.main_pool.download_image_from_fullres(tr_event, event.target.closest('img#pic_fullres_preview'))}
	if (event.target.closest('flist-entry.media_entry.mde_vid')){window.bootlegger.main_pool.video_dl(tr_event, event.target.closest('flist-entry.media_entry.mde_vid'))}


});


document.addEventListener('keydown', tr_event => {


	// ==========================================
	// 	main_pool main_pool
	// ==========================================

	if (event.target.closest('body')){window.bootlegger.main_pool.img_cycle_lr(tr_event, event.target.closest('body'))}
	if (event.target.closest('body')){window.bootlegger.main_pool.select_all_in_folder(tr_event)}
	if (event.target.closest('body')){window.bootlegger.main_pool.toggle_webm_play(tr_event)}
	if (event.target.closest('body')){window.bootlegger.main_pool.webm_skip_lr(tr_event)}
	if (event.target.closest('body')){window.bootlegger.main_pool.close_webm_preview(tr_event)}


});


document.addEventListener('mousemove', tr_event => {


	// ==========================================
	// 	main_pool main_pool
	// ==========================================

	if (event.target.closest('flist-entry.frames_processed etype[vid]')){window.bootlegger.main_pool.vidscroll(tr_event, event.target.closest('flist-entry.frames_processed etype[vid]'))}


});


document.addEventListener('wheel', tr_event => {


	// ==========================================
	// 	main_pool main_pool
	// ==========================================

	if (event.target.closest('body')){window.bootlegger.main_pool.mwheel_adjust_volume(tr_event)}


});


