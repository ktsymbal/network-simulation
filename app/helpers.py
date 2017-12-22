from io import BytesIO

from flask import make_response
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from app import app


def plot(func):
    def wrapper():
        message_sizes = app.config['MESSAGE_SIZES']
        packet_sizes = app.config['PACKET_SIZES']
        network = app.config['NETWORK']
        fig = Figure()
        func(fig, message_sizes, packet_sizes, network)
        fig.tight_layout()
        canvas = FigureCanvasAgg(fig)
        output = BytesIO()
        canvas.print_png(output)
        response = make_response(output.getvalue())
        response.mimetype = 'image/png'
        return response
    return wrapper