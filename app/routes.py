from flask import render_template, jsonify, request

from app import app
from app.exceptions import NoSuchLink
from app.forms import SendMessageForm


@app.route('/', methods=['GET', 'POST'])
def network():
    form = SendMessageForm()
    nodes_choices = [(node.id, str(node)) for node in app.config['NETWORK'].nodes]
    form.source.choices = nodes_choices
    form.target.choices = nodes_choices
    result = None
    if form.validate_on_submit():
        args = [form.source.data, form.target.data, form.message_size.data, form.packet_size.data]
        if form.virtual_circuit.data:
            result = app.config['NETWORK'].virtual_circuit(*args)
        elif form.datagram.data:
            result = app.config['NETWORK'].datagram(*args)
    return render_template('index.html', form=form, result=result)


@app.route('/nodes')
def nodes():
    return jsonify(app.config['NETWORK'].nodes_for_frontend())


@app.route('/links')
def links():
    return jsonify(app.config['NETWORK'].links_for_frontend())


@app.route('/link')
def link_details():
    link_id = request.args.get('link_id')
    try:
        return_obj = app.config['NETWORK'].get_link_by_id(int(link_id)).representation_for_frontend()
    except NoSuchLink:
        return_obj = None
    return jsonify(return_obj)


@app.route('/update-link', methods=['POST'])
def update_link():
    app.config['NETWORK'].update_link(request.data)


@app.route('/routing-table')
def routing_table():
    node_id = request.args.get('node_id')
    try:
        return_obj = app.config['NETWORK'].get_node_by_id(int(node_id)).get_routing_table_str()
    except NoSuchLink:
        return_obj = None
    return jsonify(return_obj)

