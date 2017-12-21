from math import sin, radians, cos, ceil

from app.network.constants import NODES_NUMBER


class Node:
    def __init__(self, id, network_id):
        self.id = id
        self.network_id = network_id
        self.neighbours = {}
        self.routing_table = {}
        self.x, self.y = self.calculate_xy()

    def add_neighbour_node(self, neighbour_node, link):
        self.neighbours[neighbour_node] = link

    def calculate_xy(self):
        radius = 200
        angle = (self.id - NODES_NUMBER * self.network_id) * int(360 / NODES_NUMBER)

        def calculate_x():
            center_x = 300 if self.network_id % 2 == 0 else 1000
            return center_x + radius * sin(radians(angle))

        def calculate_y():
            center_y = 300 if self.network_id < 2 else 800
            return center_y + radius * cos(radians(angle))

        return tuple(map(int, [calculate_x(), calculate_y()]))

    def representation_for_frontend(self):
        return {
            'id': self.id,
            'label': self.id,
            'group': self.network_id,
            'x': self.x,
            'y': self.y,
        }

    def get_routing_table_str(self):
        return {str(node): {'path': list(map(str, path_info['path'])), 'cost': ceil(path_info['cost'])}
                for node, path_info in self.routing_table.items()}

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.id)