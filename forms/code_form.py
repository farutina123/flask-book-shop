from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired, Length


class CodeForm(FlaskForm):
    code = StringField('SMS', validators=[InputRequired(), Length(max=4, min=4)])