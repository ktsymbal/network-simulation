from math import floor, ceil
from random import choice

import math
import matplotlib.pyplot as plt
import networkx as nx
from cached_property import cached_property

from app.exceptions import NoSuchLink, NoSuchNode
from app.network.constants import REGIONAL_NETWORKS_NUMBER, NODES_NUMBER, LINK_WEIGHTS, LinkType, NODE_DEGREE
from app.network.node import Node
from app.network.supervisor import Supervisor

from app.network.link import Link


class Network:
    SPEED = 500
    HEADER_SIZE = 60
    SERVICE_PACKET_SIZE = 100

    def __init__(self):
        self.nodes = []
        self.links = []
        self.regional_networks_number = REGIONAL_NETWORKS_NUMBER
        self.create_nodes()
        self.generate_network()
        self.supervisor = Supervisor(self)

    @cached_property
    def regional_networks(self):
        """
        A list of tuples containing regional networks nodes
        """
        regional_networks = []
        for i in range(1, self.regional_networks_number + 1):
            regional_networks.append(tuple(filter(lambda node: node.network_id == i, self.nodes)))
        return regional_networks

    def __iter__(self):
        for node in self.nodes:
            yield node

    def generate_network(self):
        self.generate_links_between_regional_networks()
        # Number of edges in regional network to satisfy the number of nodes and the average node degree
        number_of_edges = floor(NODES_NUMBER * NODE_DEGREE / 2)

        for regional_network in self.regional_networks:
            edges_left = number_of_edges
            # Create at least one edge for every node
            for node1 in regional_network:
                if not node1.neighbours or next(iter(node1.neighbours.values())).type == LinkType.SATELLITE:
                    node2 = self.get_non_adjacent_node(node1, regional_network)
                    self.add_link(node1, node2)
                    edges_left -= 1

            # Create other random links
            while edges_left:
                node1 = choice(regional_network)
                node2 = self.get_non_adjacent_node(node1, regional_network)
                self.add_link(node1, node2)
                edges_left -= 1

    @staticmethod
    def get_non_adjacent_node(node, set_of_nodes):
        node2 = node
        while node2 == node or node in node2.neighbours:
            node2 = choice(set_of_nodes)
        return node2

    def generate_links_between_regional_networks(self):
        """
        Create satellite links between regional networks.
        :return: None
        """
        for i, regional_network1 in enumerate(self.regional_networks):
            for regional_network2 in self.regional_networks[i + 1:]:
                self.add_link(choice(regional_network1), choice(regional_network2), type=LinkType.SATELLITE)

    def create_nodes(self):
        for regional_network_id in range(REGIONAL_NETWORKS_NUMBER):
            for node_id in range(NODES_NUMBER):
                self.add_node(regional_network_id * NODES_NUMBER + node_id + 1, regional_network_id + 1)

    def virtual_circuit(self, source_id, target_id, message_size, packet_size):
        source = self.get_node_by_id(source_id)
        target = self.get_node_by_id(target_id)
        path = source.routing_table[target]['path']
        transitions = len(path) - 1

        data_packets_number = math.ceil(message_size / (packet_size - self.HEADER_SIZE)) * transitions
        service_packets_number = 2 * transitions * (data_packets_number + 1)
        data_traffic = data_packets_number * packet_size
        service_traffic = service_packets_number * self.SERVICE_PACKET_SIZE
        traffic = data_traffic + service_traffic

        time = 0
        for i, node in enumerate(path[:-1]):
            link = node.neighbours[path[i + 1]]
            time += (traffic / self.SPEED) * link.type.value* link.weight

        return {
            'mode': 'virtual_circuit',
            'source_id': source_id,
            'target_id': target_id,
            'service_packets': service_packets_number,
            'service_traffic': service_traffic,
            'data_packets': data_packets_number,
            'data_traffic': data_traffic,
            'time': int(time),
            'path': [node.id for node in path],
            'traffic': traffic
        }

    def datagram(self, source_id, target_id, message_size, packet_size):
        source = self.get_node_by_id(source_id)
        target = self.get_node_by_id(target_id)
        path = source.routing_table[target]['path']
        transitions = len(path) - 1

        data_packets_number = math.ceil(message_size / (packet_size - self.HEADER_SIZE)) * transitions
        service_packets_number = transitions * data_packets_number
        data_traffic = data_packets_number * packet_size
        service_traffic = service_packets_number * self.SERVICE_PACKET_SIZE
        traffic = data_traffic + service_traffic

        time = 0
        for i, node in enumerate(path[:-1]):
            link = node.neighbours[path[i + 1]]
            time += (traffic / self.SPEED) * link.type.value * link.weight

        return {
            'mode': 'datagram',
            'source_id': source_id,
            'target_id': target_id,
            'service_packets': service_packets_number,
            'service_traffic': service_traffic,
            'data_packets': data_packets_number,
            'data_traffic': data_traffic,
            'time': int(time),
            'path': [node.id for node in path],
            'traffic': traffic
        }

    def add_node(self, node_id, network_id):
        node = Node(node_id, network_id)
        self.nodes.append(node)
        return node

    def add_link(self, node1, node2, weight=None, type=None, recalculate_routing_tables=False):
        if not weight:
            if type == LinkType.SATELLITE:
                weight = choice(LINK_WEIGHTS[-3:])
            else:
                weight = choice(LINK_WEIGHTS)

        if not type:
            if node1.network_id != node2.network_id:
                type = LinkType.SATELLITE
            else:
                type = choice([LinkType.DUPLEX, LinkType.HALF_DUPLEX])
        try:
            new_id = self.links[-1].id + 1
        except IndexError:
            new_id = 1
        link = Link(new_id, node1, node2, type, weight)
        self.links.append(link)
        node1.add_neighbour_node(node2, link)
        node2.add_neighbour_node(node1, link)
        if recalculate_routing_tables:
            self.supervisor.take_over_network()
        return link

    def user_add_link(self, node1_id, node2_id):
        try:
            node1 = self.get_node_by_id(node1_id)
        except NoSuchNode:
            node1 = None
        try:
            node2 = self.get_node_by_id(node2_id)
        except NoSuchNode:
            node2 = None

        if not (node1 and node2):
            if not (node1 or node2):
                self.regional_networks_number += 1
                node1 = self.add_node(node1_id, self.regional_networks_number)
                node2 = self.add_node(node2_id, self.regional_networks_number)
            elif not node1:
                node1 = self.add_node(node1_id, node2.network_id)
            elif not node2:
                node2 = self.add_node(node2_id, node1.network_id)

        return self.add_link(node1, node2, recalculate_routing_tables=True)

    def nodes_for_frontend(self):
        return [node.representation_for_frontend() for node in self.nodes]

    def links_for_frontend(self):
        return [link.representation_for_frontend() for link in self.links]

    def get_node_by_id(self, id):
        """
        Search for a link with id. If it doesn't exist, raise NoSuchLink exception.
        """
        try:
            node = self.nodes[id - 1]
        except IndexError:
            raise NoSuchNode(id)

        try:
            return node if node.id == id else list(filter(lambda l: l.id == id, self.nodes))[0]
        except IndexError:
            raise NoSuchNode(id)

    def get_link_by_id(self, id):
        """
        Search for a link with id. If it doesn't exist, raise NoSuchLink exception.
        """
        link = self.links[id - 1]
        try:
            return link if link.id == id else list(filter(lambda l: l.id == id, self.links))[0]
        except IndexError:
            raise NoSuchLink(id)

    def update_link(self, link_dict):
        try:
            self.get_link_by_id(int(link_dict['id'])).update_from_dict(link_dict)
            self.supervisor.take_over_network()
        except NoSuchLink:
            pass

    def delete_link(self, link_id, recalculate_routing_tables=True):
        try:
            link = self.get_link_by_id(link_id)
        except NoSuchLink:
            return
        del self.links[self.links.index(link)]
        del link.node1.neighbours[link.node2]
        del link.node2.neighbours[link.node1]
        if recalculate_routing_tables:
            self.supervisor.take_over_network()

    def delete_node(self, node_id):
        try:
            node = self.get_node_by_id(node_id)
        except NoSuchNode:
            return

        for neighbour, link in list(node.neighbours.items()):
            self.delete_link(link.id, recalculate_routing_tables=False)

        del self.nodes[self.nodes.index(node)]
        self.supervisor.take_over_network()


if __name__ == '__main__':
    network = Network()
    G = nx.Graph()
    G.add_nodes_from(network.nodes)
    G.add_edges_from([(link.node1, link.node2, {'weight': link.weight}) for link in network.links])
    options = {
        'node_color': 'blue',
        'node_size': 70,
        'font_size': 7,
        'width': 1,
        'with_labels': True,
    }
    plt.subplot(121)
    nx.draw(G, **options)
    print(sum([len(node.neighbours) for node in network.nodes]) / len(network.nodes))
    print(network.nodes)
    print(network.links)
    random_node = choice(network.nodes)
    print(random_node.routing_table)
    plt.show()
