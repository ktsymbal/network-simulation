from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired


class SendMessageForm(FlaskForm):
    message_size = IntegerField('Message size', validators=[DataRequired()], default=5000)
    packet_size = IntegerField('Packet size', validators=[DataRequired()], default=500)
    source = SelectField('Source', validators=[DataRequired()], coerce=int)
    target = SelectField('Target', validators=[DataRequired()], coerce=int)
    virtual_circuit = SubmitField('Virtual circuit mode')
    datagram = SubmitField('Datagram mode')