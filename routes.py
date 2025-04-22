from flask import Blueprint, flash, redirect, url_for, render_template, request
from flask_login import login_user, login_required, current_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length, Email, EqualTo
from db.database import session_scope
from db.models import User
from werkzeug.security import generate_password_hash, check_password_hash
import random
import email_validator
from click import confirm
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


@main_blueprint.route('register', methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        with session_scope() as session:
            user = session.query(User).filter_by(email=form.email.data).first()
        if user:
            flash('User with this email already exists', category='danger')
            return redirect(url_for('main.register', form=form))
        user = User(username = form.username.data,
                    email = form.email.data,
                    password_hash = generate_password_hash(form.password.data))
        with session_scope() as session:
            session.add(user)
        return redirect(url_for('main.login'))
    elif form.errors:
        flash(form.errors, category='danger')
    return render_template('register.html', form=form)


@main_blueprint.route('/main')
@login_required
def main_route():
    return render_template('home.html', name = current_user.username)


@main_blueprint.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        with session_scope() as session:
            user = session.query(User).filter_by(email=form.email.data).first()
            if user and check_password_hash(user.password_hash, form.password.data):
                code = ''.join(random.sample([str(x) for x in range(10)], 4))
                form_code = CodeForm()
                return render_template('enter_code.html', code=code, form=form_code, user_email=user.email)
        flash('Login failed', 'danger')
    return render_template('login.html', form=form)


@main_blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.login'))