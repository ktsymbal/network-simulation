import os

from app.network.network import Network

base_dir = os.path.abspath(os.path.dirname(__file__))
NETWORK = Network()
SECRET_KEY = 'kjbghcfaxtjgsyuhdjoieofe6556789dhnshus4d87w'