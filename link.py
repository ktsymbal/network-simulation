class Link:
    def __init__(self, node1, node2, type, weight):
        self.node1 = node1
        self.node2 = node2
        self.type = type
        self.weight = type.value * weight

    def __repr__(self):
        return str(self)

    def __str__(self):
        return '%s %s-%s %s' % (self.type.name, self.node1, self.node2, self.weight)