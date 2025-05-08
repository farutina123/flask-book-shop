from flask_wtf import FlaskForm
from wtforms import RadioField


class OrderForm(FlaskForm):
    type_address = RadioField('выберите способ доставки', choices=[
        ('self', 'самовывоз'), ('door', 'до двери')])