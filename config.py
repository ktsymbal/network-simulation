import os

from app.network.network import Network

base_dir = os.path.abspath(os.path.dirname(__file__))
NETWORK = Network()
MESSAGE_SIZES = [10000, 20000, 30000, 40000, 50000]
PACKET_SIZES = [296, 508, 1006, 1500, 2002, 4352, 8166, 17914]
SECRET_KEY = 'kjbghcfaxtjgsyuhdjoieofe6556789dhnshus4d87w'