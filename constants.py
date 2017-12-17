from enum import Enum

REGIONAL_NETWORKS_NUMBER = 3
NODE_DEGREE = 3.5
NODES_NUMBER = 9
LINK_WEIGHTS = (2, 4, 5, 7, 8, 12, 15, 17, 18, 22, 25, 32)


class LinkType(Enum):
    DUPLEX = 1
    HALF_DUPLEX = 1.8
    SATELLITE = 3