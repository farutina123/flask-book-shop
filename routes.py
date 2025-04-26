from flask import Blueprint, flash, redirect, url_for, render_template, request
from flask_login import login_user, login_required, current_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length, Email, EqualTo
from db.database import session_scope
from db.models import User, Book, Genre
from werkzeug.security import generate_password_hash, check_password_hash
import random
import email_validator
from click import confirm
import json
from sqlalchemy import cast, String

main_blueprint = Blueprint('main', __name__, url_prefix='/')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(max=100, min=4)])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=36)])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo("password")])


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=36)])


class CodeForm(FlaskForm):
    code = StringField('SMS', validators=[InputRequired(), Length(max=4, min=4)])


@main_blueprint.route('/enter_code/<code>/<user_email>', methods=["GET", "POST"])
def enter_code(code, user_email):
    form = CodeForm()
    if form.validate_on_submit():
        with session_scope() as session:
            user = session.query(User).filter_by(email=user_email).first()
            if code == form.code.data:
                login_user(user=user)
                return redirect(url_for('main.main_route'))
            else:
                flash("код смс не верный", 'danger')
                return redirect(url_for('main.login'))
    elif form.errors:
        flash(form.errors, category='danger')
    return render_template('enter_code.html', form=form)


@main_blueprint.route('/enter_code/<code>/<user_email>/<user_name>/<user_hash>', methods=["GET", "POST"])
def enter_code_register(code, user_email, user_name, user_hash):
    form = CodeForm()
    if form.validate_on_submit():
        if code == form.code.data:
            user = User(username = user_name,
                        email = user_email,
                        password_hash = user_hash)
            with session_scope() as session:
                session.add(user)
                session.commit()
                login_user(user=user)
            return redirect(url_for('main.main_route'))
        else:
            flash("код смс не верный", 'danger')
            return redirect(url_for('main.login'))
    elif form.errors:
        flash(form.errors, category='danger')
    return render_template('enter_code_register.html', form=form)


@main_blueprint.route('register', methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        with session_scope() as session:
            user = session.query(User).filter_by(email=form.email.data).first()
        if user:
            flash('User with this email already exists', category='danger')
            return redirect(url_for('main.register', form=form))
        code = ''.join(random.sample([str(x) for x in range(10)], 4))
        form_code = CodeForm()
        return render_template('enter_code_register.html', code=code, form=form_code,
                               user_email=form.email.data, user_name=form.username.data, user_hash=generate_password_hash(form.password.data))
    elif form.errors:
        flash(form.errors, category='danger')
    return render_template('register.html', form=form)


@main_blueprint.route('/')
def not_log():
    with open('books_catalog.json', encoding='utf-8') as f:
        data = json.load(f)
    for item in data:
        with session_scope() as session:
            book = session.query(Book).filter_by(title=item['title'], author=item['author']).first()
            if book:
                continue
            book = Book(title=item['title'], author=item['author'], price=item['price'], genre=item['genre'],
                    cover=item['cover'], description=item['description'], rating=item['rating'], year=item['year'])
            session.add(book)
        with session_scope() as session:
            genre = session.query(Genre).filter_by(title=item['genre']).first()
            if not genre:
                genre = Genre(title=item['genre'])
                session.add(genre)
    with session_scope() as session:
        genre_list = session.query(Genre)
        books = session.query(Book)
        list_id = []
        rand_books = []
        for item in books:
            list_id.append(item.id)
        rand_books_id = random.sample(list_id, 3)
        for item in rand_books_id:
            rand_books.append(session.query(Book).filter(cast(Book.id, String) == item).first())
        return render_template('not_log.html', genres=genre_list, top=rand_books)


@main_blueprint.route('/main')
@login_required
def main_route():
    with session_scope() as session:
        genre_list = session.query(Genre)
    return render_template('home.html', genres=genre_list)


@main_blueprint.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        with session_scope() as session:
            user = session.query(User).filter_by(email=form.email.data).first()
            if user and check_password_hash(user.password_hash, form.password.data):
                code = ''.join(random.sample([str(x) for x in range(10)], 4))
                form_code = CodeForm()
                print(user)
                print(user.email)
                return render_template('enter_code.html', code=code, form=form_code, user_email=user.email)
        flash('Login failed', 'danger')
    return render_template('login.html', form=form)


@main_blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.not_log'))