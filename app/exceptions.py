class NoSuchLink(Exception):
    def __init__(self, id):
        self.message = "There is no link with id=%s" % id


class NoSuchNode(Exception):
    def __init__(self, id):
        self.message = "There is no node with id=%s" % id