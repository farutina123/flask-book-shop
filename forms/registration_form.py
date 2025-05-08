from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length, Email, EqualTo


class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[InputRequired(), Length(max=100, min=4)])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Пароль', validators=[InputRequired(), Length(min=8, max=36)])
    confirm_password = PasswordField('Повторите пароль', validators=[InputRequired(), EqualTo("password")])