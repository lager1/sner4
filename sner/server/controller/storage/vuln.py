"""controller vuln"""

from datatables import ColumnDT, DataTables
from flask import jsonify, redirect, render_template, request, url_for
from sqlalchemy.sql import func

from sner.server import db
from sner.server.controller.storage import blueprint, render_host_address
from sner.server.form import ButtonForm
from sner.server.form.storage import IdsForm, TagByIdForm, VulnForm
from sner.server.model.storage import Host, Service, Vuln


@blueprint.app_template_filter()
def url_for_ref(ref):
	"""generate anchor url for vuln.ref"""

	try:
		rtype, rval = ref.split('-', maxsplit=1)
	except ValueError:
		return '#'

	url = '#'
	if rtype == 'URL':
		url = rval
	elif rtype == 'CVE':
		url = 'https://cvedetails.com/cve/CVE-%s' % rval
	elif rtype == 'NSS':
		url = 'https://www.tenable.com/plugins/nessus/%s' % rval
	elif rtype == 'BID':
		url = 'http://www.securityfocus.com/bid/%s' % rval
	elif rtype == 'CERT':
		url = 'https://www.kb.cert.org/vuls/id/%s' % rval
	elif rtype == 'EDB':
		url = 'https://www.exploit-db.com/exploits/%s' % rval.replace('ID-', '')
	elif rtype == 'SN':
		url = url_for('storage.note_view_route', note_id=rval)

	return url


@blueprint.app_template_filter()
def text_for_ref(ref):
	"""generate anchor text for vuln.ref"""

	try:
		rtype, _ = ref.split('-', maxsplit=1)
	except ValueError:
		return ref

	return 'URL' if rtype == 'URL' else ref


@blueprint.route('/vuln/list')
def vuln_list_route():
	"""list vulns"""

	return render_template('storage/vuln/list.html')


@blueprint.route('/vuln/list.json', methods=['GET', 'POST'])
def vuln_list_json_route():
	"""list vulns, data endpoint"""

	columns = [
		ColumnDT('1', mData='_select', search_method='none', global_search=False),
		ColumnDT(Vuln.id, mData='id'),
		ColumnDT(Host.id, mData='host_id'),
		ColumnDT(Host.address, mData='host_address'),
		ColumnDT(Host.hostname, mData='host_hostname'),
		ColumnDT(func.concat_ws('/', Service.port, Service.proto), mData='service'),
		ColumnDT(Vuln.name, mData='name'),
		ColumnDT(Vuln.xtype, mData='xtype'),
		ColumnDT(func.text(Vuln.severity), mData='severity'),
		ColumnDT(Vuln.refs, mData='refs'),
		ColumnDT(Vuln.tags, mData='tags'),
		ColumnDT(Vuln.comment, mData='comment'),
		ColumnDT('1', mData='_buttons', search_method='none', global_search=False)
	]
	query = db.session.query().select_from(Vuln).join(Host, Vuln.host_id == Host.id).outerjoin(Service, Vuln.service_id == Service.id)

	## filtering
	if 'host_id' in request.values:
		query = query.filter(Vuln.host_id == request.values.get('host_id'))

	vulns = DataTables(request.values.to_dict(), query, columns).output_result()
	return jsonify(vulns)


@blueprint.route('/vuln/add/<model_name>/<model_id>', methods=['GET', 'POST'])
def vuln_add_route(model_name, model_id):
	"""add vuln to host or service"""

	(host, service) = (None, None)
	if model_name == 'host':
		host = Host.query.get(model_id)
	elif model_name == 'service':
		service = Service.query.get(model_id)
		host = service.host
	form = VulnForm(host_id=host.id, service_id=(service.id if service else None))

	if form.validate_on_submit():
		vuln = Vuln()
		form.populate_obj(vuln)
		db.session.add(vuln)
		db.session.commit()
		return redirect(url_for('storage.host_view_route', host_id=vuln.host_id))

	return render_template(
		'storage/vuln/addedit.html',
		form=form,
		form_url=url_for('storage.vuln_add_route', model_name=model_name, model_id=model_id),
		host=host,
		service=service)


@blueprint.route('/vuln/edit/<vuln_id>', methods=['GET', 'POST'])
def vuln_edit_route(vuln_id):
	"""edit vuln"""

	vuln = Vuln.query.get(vuln_id)
	form = VulnForm(obj=vuln)

	if form.validate_on_submit():
		form.populate_obj(vuln)
		db.session.commit()
		return redirect(url_for('storage.host_view_route', host_id=vuln.host_id))

	return render_template(
		'storage/vuln/addedit.html',
		form=form,
		form_url=url_for('storage.vuln_edit_route', vuln_id=vuln_id),
		host=vuln.host,
		service=vuln.service)


@blueprint.route('/vuln/delete/<vuln_id>', methods=['GET', 'POST'])
def vuln_delete_route(vuln_id):
	"""delete vuln"""

	vuln = Vuln.query.get(vuln_id)
	form = ButtonForm()
	if form.validate_on_submit():
		db.session.delete(vuln)
		db.session.commit()
		return redirect(url_for('storage.host_view_route', host_id=vuln.host_id))

	return render_template('button-delete.html', form=form, form_url=url_for('storage.vuln_delete_route', vuln_id=vuln_id))


@blueprint.route('/vuln/view/<vuln_id>')
def vuln_view_route(vuln_id):
	"""view vuln"""

	vuln = Vuln.query.get(vuln_id)
	return render_template('storage/vuln/view.html', vuln=vuln, button_form=ButtonForm())


@blueprint.route('/vuln/delete_by_id', methods=['POST'])
def vuln_delete_by_id_route():
	"""delete multiple vulns route"""

	form = IdsForm()
	if form.validate_on_submit():
		try:
			Vuln.query.filter(Vuln.id.in_([tmp.data for tmp in form.ids.entries])).delete(synchronize_session=False)
			db.session.commit()
			return jsonify({'status': 200})
		except Exception as e:
			db.session.rollback()
			return jsonify({'status': 400, 'title': 'Action failed', 'detail': str(e)}), 400

	return jsonify({'status': 400, 'title': 'Invalid form submitted.'}), 400


@blueprint.route('/vuln/tag_by_id', methods=['POST'])
def vuln_tag_by_id_route():
	"""tag multiple route"""

	form = TagByIdForm()
	if form.validate_on_submit():
		try:
			tag = form.tag.data
			for vuln in Vuln.query.filter(Vuln.id.in_([tmp.data for tmp in form.ids.entries])).all():
				vuln.tags = list(set((vuln.tags or []) + [tag]))
			db.session.commit()
			return jsonify({'status': 200})
		except Exception as e:
			db.session.rollback()
			return jsonify({'status': 400, 'title': 'Action failed', 'detail': str(e)}), 400

	return jsonify({'status': 400, 'title': 'Invalid form submitted.'}), 400