from flask_wtf import FlaskForm
from wtforms import TextAreaField, RadioField
from wtforms.validators import InputRequired, Length


class ReviewForm(FlaskForm):
    rating = RadioField('оценка', choices=[
        ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')])
    review = TextAreaField('Ваш отзыв', validators=[InputRequired(), Length(max=200, min=4)])