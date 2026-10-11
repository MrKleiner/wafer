
const base64ToUint8Array = function(base64) {
	const binary = atob(base64);
	const bytes = new Uint8Array(binary.length);

	for (let i = 0; i < binary.length; i++) {
		bytes[i] = binary.charCodeAt(i);
	}

	return bytes;
}

const decompress = async function(bytes) {
	const ds = new DecompressionStream('deflate');
	const writer = ds.writable.getWriter();

	writer.write(bytes);
	writer.close();

	return new TextDecoder().decode(
		await new Response(ds.readable).arrayBuffer()
	);
}

const trow = function(row_data){
	const trow_dom = document.createElement('div');
	trow_dom.classList.add('trow');
	for (const tcol of row_data){
		const tcol_dom = document.createElement('div');
		tcol_dom.classList.add('tcol');
		tcol_dom.textContent = tcol;
		trow_dom.append(tcol_dom);
	}
	return trow_dom
}

const main = async function(){
	const tables = JSON.parse(
		await decompress(base64ToUint8Array(`@tables@`).buffer)
	);

	for (const table_data of tables){
		const table_dom = document.createElement('div');
		table_dom.classList.add('table');

		const table_name = document.createElement('div');
		table_name.classList.add('table_name');
		table_name.textContent = table_data.tname;
		table_dom.append(table_name);

		const table_header = trow(table_data.layout);
		table_header.classList.add('table_header');
		table_dom.append(table_header);

		const table_contents = document.createElement('div');
		table_contents.classList.add('table_contents');

		for (const row_data of table_data.content){
			table_contents.append(trow(row_data));
		}

		table_dom.append(table_contents);

		document.body.append(table_dom);
	}

	for (const table of document.querySelectorAll('.table')){
		const sizes = {};
		for (const trow of table.querySelectorAll('.table_contents .trow')){
			let idx = 0;
			for (const tcol of trow.querySelectorAll('.tcol')){
				if (!(idx in sizes)){
					sizes[idx] = 0;
				}

				if (tcol.textContent.length > sizes[idx]){
					sizes[idx] = tcol.textContent.length;
				}

				idx += 1;
			}
		}

		const thinnify = [];
		for (const [idx, size] of Object.entries(sizes)){
			if (size < 6){
				thinnify.push(idx);
			}
		}

		for (const trow of table.querySelectorAll('.trow')){
			const cols = trow.querySelectorAll('.tcol');
			for (idx of thinnify){
				cols[idx].classList.add('thin');
			}

			for (const col of cols){
				col.style.width = `${((93 - (thinnify.length * 4)) / (cols.length - thinnify.length))}vw`;
			}
		}
	}

	const largePreview = document.querySelector('#large_preview');

	const toggleHighlight = function(state){
		document.body.classList.toggle('hlight', state);
		if (state){
			largePreview.style.display = '';
		}else{
			largePreview.style.display = 'none';
		}
	}

	toggleHighlight(false);

	document.addEventListener('mouseover', function(evt){
		if (evt.target.closest('.tcol')){
			largePreview.textContent = evt.target.closest('.tcol').textContent;
		}
	})

	document.addEventListener('keydown', function(evt){
		if (evt.altKey){
			evt.preventDefault();
			toggleHighlight(true);
		}
	})

	document.addEventListener('keyup', function(evt){
		if (evt.key == 'Alt'){
			evt.preventDefault();
			toggleHighlight(false);
		}
	})
}

main()
