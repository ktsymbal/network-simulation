from math import inf


class Supervisor:
    def __init__(self, network):
        self.network = network
        self.routing_tables = {}
        self.take_over_network()

    def take_over_network(self):
        for node in self.network:
            node.routing_table = self.generate_node_routing_table(node)
            self.routing_tables[node] = node.routing_table

    def generate_node_routing_table(self, node):
        routing_table = {}
        dijkstra_result = self.dijkstra_algorithm(self.network, node)
        for n, path_info in dijkstra_result.items():
            path = []
            cost = 0
            previous_node = n
            while previous_node:
                cost += path_info[0]
                path.append(previous_node)
                previous_node = dijkstra_result[previous_node][1]
            routing_table[n] = {'path': list(reversed(path)), 'cost': cost}
        return routing_table

    @staticmethod
    def dijkstra_algorithm(network, node):
        visited = set()
        to_visit = {node}
        # Initialise the result table with distance set to infinity and previous node in the shortest path set to None
        table = {n: [inf, None] for n in network}
        table[node] = [0, None]

        while to_visit:
            current_node = to_visit.pop()
            for n, l in current_node.neighbours.items():
                if n not in visited:
                    current_distance = table[current_node][0] + l.weight
                    if current_distance < table[n][0]:
                        table[n] = [current_distance, current_node]
                    to_visit.add(n)
            visited.add(current_node)

        return table