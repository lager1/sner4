/* This file is part of sner4 project governed by MIT license, see the LICENSE.txt file. */

/*
 * sner ui function bundled to simple modules
 *
 * NOTE: While the functions are groupped to ES6 classes, it turns out that the concept of classes 
 * is not very sound in javascript. The main issue might arise when using `this` which is very
 * soft concept here. On the first occurence of troubles (datatables callback this(dt instance)
 * vs. event callbacks this(event element) we should fall back to Revealing Module Pattern immediatelly.
 */

class SnerDatatablesModule {
	/**
	 * default ajaxed datatables options
	 */
	ajax_options = {
		// general settings
		'serverSide': true,
		'processing': true,

		// visuals
		'dom': '<"row"<"col-sm-6"l><"col-sm-6"f>> <"row"<"col-sm-12"p>> <"row"<"col-sm-12"rt>> <"row"<"col-sm-6"i><"col-sm-6"p>>',
		'info': true,
		'paging': true,
		'pageLength': 50,
		'lengthMenu': [ 10, 50, 100, 200, 500, 1000 ],

		// behaviors
		'drawCallback': function (settings) {
			// note this holds a datatable instance here
			Sner.dt.toggle_pagination(this.api());
			this.find('td a.abutton_delete_by_url').on('click', {'dt': this.api(), 'confirmation': 'Really delete?'}, Sner.action_submit_by_url);
		},
		'stateSave': true,
		// paging might get broken when transiting from high page of non-filtered table to filtered one with few row, state key must reflect the filter
		'stateSaveCallback': function(settings,data) {
			sessionStorage.setItem('DataTables_'+settings.sInstance+'_'+window.location.pathname+'_'+window.location.search, JSON.stringify(data));
		},
		'stateLoadCallback': function(settings) {
			return JSON.parse(sessionStorage.getItem('DataTables_'+settings.sInstance+'_'+window.location.pathname+'_'+window.location.search));
		}
	};

	/**
	 * default static datatables options
	 */
	static_options = {
		'columnDefs': [ {
			'targets': 'no-sort',
			'orderable': false,
		} ],
		'order': [[0, 'asc']],
		'paging': false,
		'info': false
	};

	/**
	 * generate object with default column options and non-html rendering
	 *
	 * @param {string} d - column name
	 * @param {object} extra - extra data to inject into column definition
	 */
	column(d, extra={}) {
		return $.extend({'name': d, 'title': d, 'data': d, 'render': $.fn.dataTable.render.text()}, extra);
	}

	/**
	 * generate _select column definition
	 */
	column_select() {
		return {'name': '_select', 'title': '', 'data': null, 'defaultContent': '', 'orderable': false, 'className': 'select-checkbox'};
	}

	/**
	 * generate _select column definition
	 * @param {callback} render - function to render cell, typically compiled hbs template
	 */
	column_buttons(render_callback=null, extra={}) {
		return $.extend(
			{'name': '_buttons', 'title': '_buttons', 'data': '_buttons', 'orderable': false, 'className': 'dt-nowrap', 'render': function(data, type, row, meta) { return render_callback(row); }},
			extra
		);
	}

	/**
	 * Select all from table
	 *
	 * @param {Object} event jquery event, event.data.dt datatable instance reference required
	 */
	selectall(event) {
		event.data.dt.rows(null, {'page': 'current'}).select();
	}

	/*
	 * Select none from table
	 *
	 * @param {Object} event jquery event, event.data.dt datatable instance reference required
	 */
	selectnone(event) {
		event.data.dt.rows(null, {'page': 'current'}).deselect();
	}

	/**
	 * toggles pagination if needed
	 *
	 * @param {object} dt - datatable instance
	 */
	toggle_pagination(dt) {
		var pagination = $('#'+dt.table().node().id+'_wrapper .dataTables_paginate');
		if (dt.page.info().pages <= 1) {
			pagination.hide();
		} else {
			pagination.show();
		}
	}

	/**
	 * returns array of selected rows/data ids
	 *
	 * @param {object} dt - datatable instance
	 */
	get_selected_ids(dt) {
		// would use .map return item[x], but it does not cleanup other row attrs
		var ids = [];
		dt.rows({'selected': true}).data().each(
			(item) => { ids.push(item['id']) }
		);
		return ids;
	}
}


class SnerModule {
	constructor() {
		this.dt = new SnerDatatablesModule();
	}

	/* WEBAUTHN UTILS */

	/**
	 * encode ArrayBuffer to base64
	 *
	 * @param  {ArrayBuffer} buffer buffer to encode
	 * @return {string}             encoded buffer
	 */
	array_buffer_to_base64(buffer) {
		return btoa(new Uint8Array(buffer).reduce((data, byte) => data + String.fromCharCode(byte), ''));
	}

	/**
	 * decode base64 data to ArrayBuffer
	 *
	 * @param  {string}      data data to decode
	 * @return {ArrayBuffer}      decoded data
	 */
	base64_to_array_buffer(data) {
		return Uint8Array.from(atob(data), c => c.charCodeAt(0)).buffer;
	}


	/* GENERAL UI HELPERS */

	/**
	 * Show global/shared modal with title and bodya
	 *
	 * @param {string} title title html fragment
	 * @param {string} body  body html fragment
	 */
	modal(title, body) {
		$('#modal-global .modal-title').html(title);
		$('#modal-global .modal-body').html(body);
		$('#modal-global').modal();
	}

	/**
	 * Will rerender hbs with context taken from data-hbs attributes.
	 * The element must contain 'data-hbs' attribute (hbs compiled template name) and 'data-hbs_context' attribute (context data encoded in json)
	 *
	 * @param {DOMElement} elem data and output enclosing element reference
	 */
	render_hbs(elem) {
		var hbs = elem.getAttribute('data-hbs');
		var context = JSON.parse(elem.getAttribute('data-hbs_context'));
		elem.innerHTML = window[hbs](context);
	}

	/**
	 * Submit form, POST data to url managing csrf token in the process.
	 *
	 * @param {string} url  target url
	 * @param {Object} data object containing data to submit
	 */
	submit_form(url, data={}) {
		data['csrf_token'] = $('meta[name="csrf-token"]').attr('content');
		return response_promise = $.ajax({"url": url,"type": "POST", "data": data})
			.fail(function(xhr, status, exception) {
				toastr.error(xhr.hasOwnProperty('responseJSON') ? xhr.responseJSON['title'] : 'Request failed'); 
			});
	}


	/* ACTION FUNCTIONS, BUTTON EVENT HANDLERS */

	/*
	 * tag multiple items
	 *
	 * @param {object} event jquery event. data required: {'dt': datatable instance, 'tag': string}
	 */
	action_tag_by_id(event) {
		var data = {
			'tag': event.target.getAttribute('data-tag'),
			'action': event.data.action
		};
		var ids = Sner.dt.get_selected_ids(event.data.dt);
		if (ids.length == 0) {
			toastr.warning('No items selected');
			return Promise.resolve();
		}
		for (var i = 0; i < ids.length; i++) { data['ids-'+i] = ids[i]; }

		Sner.submit_form(event.data.url, data)
			.always(function() { event.data.dt.draw(); });
	}

	/**
	 * delete multiple items
	 *
	 * @param {object} event jquery event. data required {'dt': datatable instance}
	 */
	action_delete_by_id(event) {
		if (!confirm('Really delete?')) { return; }

		var data = {};
		var ids = Sner.dt.get_selected_ids(event.data.dt);
		if (ids.length == 0) {
			toastr.warning('No items selected');
			return Promise.resolve();
		}
		for (var i = 0; i < ids.length; i++) { data['ids-'+i] = ids[i]; }

		Sner.submit_form(event.data.url, data)
			.always(function() { event.data.dt.draw(); });
	}

	/**
	 * submit form to data-url of an A element with confirmation dialogue
	 *
	 * @param {object} event jquery event. data required {'dt': datatable instance, 'confirmation': string}
	 */
	action_submit_by_url(event) {
		var confirmation = event.data.hasOwnProperty('confirmation') ? event.data.confirmation : 'Are you sure?';
		if (!confirm(confirmation)) { return; }

		Sner.submit_form(event.target.closest('a').getAttribute('data-url'))
			.always(function() { event.data.dt.draw(); });
	}
}

/* NOTE: should be a const, but selenium.execute_script does not recognize the library object in that case with ReferenceError */
var Sner = new SnerModule();
