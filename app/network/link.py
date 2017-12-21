from app.network.constants import LinkType


class Link:
    def __init__(self, id, node1, node2, type, weight):
        self.id = id
        self.node1 = node1
        self.node2 = node2
        self.type = type
        self.weight = type.value * weight

    def representation_for_frontend(self):
        dictionary = {
            'from': self.node1.id,
            'to': self.node2.id,
            'id': self.id,
            'type': self.type.name,
            'label': self.weight // self.type.value,
        }
        if self.type in [LinkType.SATELLITE, LinkType.HALF_DUPLEX]:
            dictionary['dashes'] = False if self.type == self.type.HALF_DUPLEX else [10, 10]
        else:
            dictionary['arrows'] = 'to;from'
        return dictionary

    def update_from_dict(self, link_dict):
        self.type = LinkType[link_dict['type']]

    def __repr__(self):
        return str(self)

    def __str__(self):
        return '%s %s-%s %s' % (self.type.name, self.node1, self.node2, self.weight)