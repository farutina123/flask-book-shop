from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms.validators import InputRequired, Length


class AddressForm(FlaskForm):
    address = TextAreaField('Ваш адрес', validators=[InputRequired(), Length(max=200, min=4)])