// let icon_index = ``
// {}



const respawn_icons = () => {
	for (let tgt of document.querySelectorAll('wafer-icon')){
		const icon_as_xml = $(icon_index[tgt.getAttribute('icname')]);
		const icon_color = tgt.getAttribute('color');
		if (icon_color){
			icon_as_xml.find('[fill]').attr('fill', icon_color);
		}
		tgt.replaceWith(icon_as_xml[0])
	}
}

const m_observer = new MutationObserver(respawn_icons)

m_observer.observe(document.body, {
	childList: true,
	subtree: true,
})

