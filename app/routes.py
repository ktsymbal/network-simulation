from io import BytesIO
from random import choice

from flask import render_template, jsonify, request, make_response
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from app import app
from app.exceptions import NoSuchLink
from app.forms import SendMessageForm
from app.helpers import plot


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
    app.config['NETWORK'].update_link(request.form)
    return jsonify({})


@app.route('/routing-table')
def routing_table():
    node_id = request.args.get('node_id')
    try:
        return_obj = app.config['NETWORK'].get_node_by_id(int(node_id)).get_routing_table_str()
    except NoSuchLink:
        return_obj = None
    return jsonify(return_obj)


@app.route('/add-connection', methods=['POST'])
def add_connection():
    link = app.config['NETWORK'].user_add_link(int(request.form['from']), int(request.form['to']))
    return jsonify(link.representation_for_frontend())


@app.route('/delete-elements', methods=['DELETE'])
def delete_elements():
    data = request.form
    try:
        nodes = data.getlist('nodes[]')
        for node_id in nodes:
            app.config['NETWORK'].delete_node(int(node_id))
        if not nodes:
            for link_id in data.getlist('edges[]'):
                app.config['NETWORK'].delete_link(int(link_id))
    except Exception as e:
        print(e)
    return jsonify({})


@app.route('/service-traffic')
def service_traffic():
    def two_plots(fig, message_sizes, packet_sizes, network):
        message = fig.add_subplot(2, 1, 1)
        message.plot(
            message_sizes,
            [network.virtual_circuit(1, 16, msg_sz, 1500)['service_traffic'] for msg_sz in message_sizes],
            '-',
            label='Віртуальний канал'
        )
        message.plot(
            message_sizes,
            [network.datagram(1, 16, msg_sz, 1500)['service_traffic'] for msg_sz in message_sizes],
            '-',
            label='Дейтаграмний'
        )
        message.legend(loc="upper left")
        message.set_ylabel('Службовий трафік, байт')
        message.set_xlabel('Розмір повідомлення, байт')

        packet = fig.add_subplot(2, 1, 2)
        packet.plot(
            packet_sizes,
            [network.virtual_circuit(1, 16, 40000, pckt_sz)['service_traffic'] for pckt_sz in packet_sizes],
            '-',
            label='Віртуальний канал'
        )
        packet.plot(
            packet_sizes,
            [network.datagram(1, 16, 40000, pckt_sz)['service_traffic'] for pckt_sz in packet_sizes],
            '-',
            label='Дейтаграмний'
        )

        packet.legend(loc="upper right")
        packet.set_xlabel('Розмір пакета, байт')
        packet.set_ylabel('Службовий трафік, байт')

    return plot(two_plots)()


@app.route('/time')
def time():
    def two_plots(fig, message_sizes, packet_sizes, network):
        packet = fig.add_subplot(2, 1, 1)
        packet.plot(
            packet_sizes,
            [network.virtual_circuit(1, 16, 30000, pckt_sz)['time'] for pckt_sz in packet_sizes],
            '-',
            label='Віртуальний канал'
        )
        packet.plot(
            packet_sizes,
            [network.datagram(1, 16, 30000, pckt_sz)['time'] for pckt_sz in packet_sizes],
            '-',
            label='Дейтаграмний'
        )
        packet.legend(loc="upper right")
        packet.set_ylabel('Час, у.о.')
        packet.set_xlabel('Розмір пакета, байт')

        transition = fig.add_subplot(2, 1, 2)
        transition_xy = {}
        node = choice(network.nodes)
        for n, path_info in node.routing_table.items():
            transitions = len(path_info['path'])
            if transitions not in transition_xy:
                virtual_circuit = network.virtual_circuit(node.id, n.id, 10000, 8166)['time']
                datagram = network.datagram(node.id, n.id, 10000, 8166)['time']
                transition_xy[transitions] = [virtual_circuit, datagram]
        transition.plot(
            sorted(transition_xy.keys()),
            [transition_xy[key][0] for key in sorted(transition_xy)],
            '-',
            label='Віртуальний канал'
        )
        transition.plot(
            sorted(transition_xy.keys()),
            [transition_xy[key][1] for key in sorted(transition_xy)],
            '-',
            label='Дейтаграмний'
        )

        transition.legend(loc="upper left")
        transition.set_xlabel('Кількість проміжних вузлів')
        transition.set_ylabel('Час, у.о.')

    return plot(two_plots)()
