from flask import Blueprint, flash, redirect, url_for, render_template
from flask_login import login_user, logout_user
from db.database import session_scope
from db.models import User
from werkzeug.security import generate_password_hash, check_password_hash
import random
from forms.login_form import LoginForm
from forms.code_form import CodeForm
from forms.registration_form import RegistrationForm

user_blueprint = Blueprint('user', __name__, url_prefix='/')


@user_blueprint.route('/enter_code/<code>/<user_email>', methods=['GET', 'POST'])
def enter_code(code, user_email):
    form = CodeForm()
    if not form.validate_on_submit():
        if form.errors:
            flash(form.errors, category='danger')
        return render_template('form/enter_code.html', form=form)
    with session_scope() as session:
        user = session.query(User).filter_by(email=user_email).first()
        if code == form.code.data:
            login_user(user=user)
            return redirect(url_for('main.main_route'))
        flash('код смс не верный', 'danger')
        return redirect(url_for('user.login'))


@user_blueprint.route('/enter_code/<code>/<user_email>/<user_name>/<user_hash>', methods=['GET', 'POST'])
def enter_code_register(code, user_email, user_name, user_hash):
    form = CodeForm()
    if not form.validate_on_submit():
        if form.errors:
            flash(form.errors, category='danger')
        return render_template('form/enter_code_register.html', form=form)
    if code != form.code.data:
        flash('код смс не верный', 'danger')
        return redirect(url_for('user.login'))
    user = User(username=user_name,
                email=user_email,
                password_hash=user_hash)
    with session_scope() as session:
        session.add(user)
        session.commit()
        login_user(user=user)
    return redirect(url_for('main.main_route'))


@user_blueprint.route('register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if not form.validate_on_submit():
        if form.errors:
            flash(form.errors, category='danger')
        return render_template('form/register.html', form=form)
    with session_scope() as session:
        user = session.query(User).filter_by(email=form.email.data).first()
        user_name = session.query(User).filter_by(username=form.username.data).first()
    if user or user_name:
        flash('User with this email or username already exists', category='danger')
        return redirect(url_for('user.register', form=form))
    code = ''.join(random.sample([str(x) for x in range(10)], 4))
    form_code = CodeForm()
    return render_template('form/enter_code_register.html', code=code, form=form_code,
                           user_email=form.email.data, user_name=form.username.data,
                           user_hash=generate_password_hash(form.password.data))


@user_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if not form.validate_on_submit():
        return render_template('form/login.html', form=form)
    with session_scope() as session:
        user = session.query(User).filter_by(email=form.email.data).first()
        if not (user and check_password_hash(user.password_hash, form.password.data)):
            flash('Login failed', 'danger')
            return render_template('form/login.html', form=form)
        code = ''.join(random.sample([str(x) for x in range(10)], 4))
        form_code = CodeForm()
        return render_template('form/enter_code.html', code=code, form=form_code, user_email=user.email)


@user_blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.not_log'))
