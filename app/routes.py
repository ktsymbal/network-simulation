from flask import render_template, jsonify, request

from app import app
from app.exceptions import NoSuchLink


@app.route('/')
def network():
    return render_template('index.html')


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
        return_obj = {}
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
        return_obj = {}
    return jsonify(return_obj)