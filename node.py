class Node:
    def __init__(self, id, network_id):
        self.id = id
        self.network_id = network_id
        self.neighbours = {}
        self.routing_table = {}

    def add_neighbour_node(self, neighbour_node, link):
        self.neighbours[neighbour_node] = link

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.id)