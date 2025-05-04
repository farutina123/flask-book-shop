from flask import Blueprint, flash, redirect, url_for, render_template, request
from flask_login import login_user, login_required, current_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, RadioField
from wtforms.validators import InputRequired, Length, Email, EqualTo
from db.database import session_scope
from db.models import User, Book, Genre, Review, CartItem, OrderItem, Order
from werkzeug.security import generate_password_hash, check_password_hash
import random
import email_validator
from click import confirm
import json
from sqlalchemy import cast, String, Integer, UUID, Uuid
from sqlalchemy.sql.expression import func, text, select
from datetime import date
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


class ReviewForm(FlaskForm):
    rating = RadioField('оценка', choices=[
        ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')])
    review = TextAreaField('Ваш отзыв', validators=[InputRequired(), Length(max=200, min=4)])


class OrderForm(FlaskForm):
    type_address = RadioField('выберите способ доставки', choices=[
        ('self', 'самовывоз'), ('door', 'до двери')])


class AddressForm(FlaskForm):
    address = TextAreaField('Ваш адрес', validators=[InputRequired(), Length(max=200, min=4)])


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


def get_random_books(session, count=3):
    random_books = session.query(Book).order_by(func.random()).limit(count).all()
    return random_books


@main_blueprint.route('/', methods=["GET", "POST"])
def not_log():
    if request.method == 'POST':
        search = request.form['search']
        with session_scope() as session:
            genre_list = session.query(Genre).all()
            filter_book = session.query(Book).filter(Book.title.ilike(f'%{search}%')).all()
            return render_template('genre_not_log.html', books_list=filter_book, title=search, genres=genre_list)
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
        rand_books = get_random_books(session, count=3)
        return render_template('not_log.html', genres=genre_list, top=rand_books)


@main_blueprint.route('/main', methods=["GET", "POST"])
@login_required
def main_route():
    if request.method == 'POST':
        search = request.form['search']
        with session_scope() as session:
            genre_list = session.query(Genre).all()
            filter_book = session.query(Book).filter(Book.title.ilike(f'%{search}%')).all()
            return render_template('genre_home.html', books_list=filter_book, title=search, genres=genre_list)
    with session_scope() as session:
        genre_list = session.query(Genre).all()
        rand_books = get_random_books(session, count=3)
        return render_template('home.html', genres=genre_list, top=rand_books)


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
    return redirect(url_for('main.not_log'))


@main_blueprint.route('/genre_log/<title_genre>', methods=["GET", "POST"])
@login_required
def group_of_genre_home(title_genre):
    if request.method == 'POST':
        search = request.form['search']
        with session_scope() as session:
            genre_list = session.query(Genre).all()
            filter_book = session.query(Book).filter(Book.title.ilike(f'%{search}%')).all()
            return render_template('genre_home.html', books_list=filter_book, title=search, genres=genre_list)
    with session_scope() as session:
        books_list = session.query(Book).filter_by(genre=title_genre)
        genre_list = session.query(Genre)
    return render_template('genre_home.html', genres=genre_list, title=title_genre, books_list=books_list)


@main_blueprint.route('/genre/<title_genre>', methods=["GET", "POST"])
def group_of_genre(title_genre):
    if request.method == 'POST':
        search = request.form['search']
        with session_scope() as session:
            genre_list = session.query(Genre).all()
            filter_book = session.query(Book).filter(Book.title.ilike(f'%{search}%')).all()
            return render_template('genre_not_log.html', books_list=filter_book, title=search, genres=genre_list)
    with session_scope() as session:
        books_list = session.query(Book).filter_by(genre=title_genre)
        genre_list = session.query(Genre)
    return render_template('genre_not_log.html', genres=genre_list, title=title_genre, books_list=books_list)


@main_blueprint.route('/book_page/<id_book>', methods=["GET", "POST"])
def book_page(id_book):
    if request.method == 'POST':
        search = request.form['search']
        with session_scope() as session:
            genre_list = session.query(Genre).all()
            filter_book = session.query(Book).filter(Book.title.ilike(f'%{search}%')).all()
            return render_template('genre_not_log.html', books_list=filter_book, title=search, genres=genre_list)
    with session_scope() as session:
        genre_list = session.query(Genre).all()
        book = session.query(Book).filter(cast(Book.id, String) == id_book).first()
        return render_template('book_page.html', book=book, genres=genre_list)

@main_blueprint.route('/book_page_review/<id_book>', methods=["GET", "POST"])
@login_required
def book_page_review(id_book):
    if request.method == 'POST':
        search = request.form['search']
        with session_scope() as session:
            genre_list = session.query(Genre).all()
            filter_book = session.query(Book).filter(Book.title.ilike(f'%{search}%')).all()
            return render_template('genre_home.html', books_list=filter_book, title=search, genres=genre_list)
    with session_scope() as session:
        genre_list = session.query(Genre).all()
        book = session.query(Book).filter(cast(Book.id, String) == id_book).first()
        book_reviews_list = session.query(Review).filter_by(book_id=id_book).all()
        if book_reviews_list:
            return render_template("book_with_review.html", genres=genre_list, book=book,
                                   list_reviews=book_reviews_list)
        return render_template('book_page_review.html', book=book, genres=genre_list)


@main_blueprint.route('/review/<id_book>', methods=["GET", "POST"])
@login_required
def review_info(id_book):
    form = ReviewForm()
    if not request.method == 'POST':
        return render_template('review.html', form=form, book=id_book)
    review = Review(review_book=form.review.data, book_id=id_book, user_id=current_user.id, rating=float(form.rating.data))
    with session_scope() as session:
        session.add(review)
    with session_scope() as session:
        book_reviews_list = session.query(Review).filter_by(book_id=id_book).all()
        res_sum = 0
        for i in book_reviews_list:
            res_sum += i.rating
        res = res_sum/len(book_reviews_list)
        session.commit()
        book = session.query(Book).filter(cast(Book.id, String) == id_book).first()
        book.rating = round(res, 2)
        session.commit()
        return redirect(url_for('main.book_page_review', id_book=book.id))


@main_blueprint.route('/buy/<id_book>/<path>')
@login_required
def buy(id_book, path):
    with session_scope() as session:
        test_book = session.query(CartItem).filter(cast(CartItem.book_id, String) == id_book, CartItem.user_id == current_user.id).first()
        if test_book:
            test_book.count += 1
        else:
            cart_item = CartItem(book_id=id_book, user_id=current_user.id)
            session.add(cart_item)
            session.commit()
    if path == 'book_page_review':
        flash('книга добавлена в корзину', 'info')
        return redirect(url_for('main.book_page_review', id_book=id_book))
    flash('книга добавлена в корзину', 'info')
    return redirect(url_for('main.main_route', id_book=id_book))


@main_blueprint.route('/buy_genre/<id_book>/<title>')
@login_required
def buy_genre(id_book, title):
    with session_scope() as session:
        test_book = session.query(CartItem).filter(cast(CartItem.book_id, String) == id_book, CartItem.user_id == current_user.id).first()
        if test_book:
            test_book.count += 1
        else:
            cart_item = CartItem(book_id=id_book, user_id=current_user.id)
            session.add(cart_item)
            session.commit()
    flash('книга добавлена в корзину', 'info')
    return redirect(url_for('main.group_of_genre_home', title_genre=title))


@main_blueprint.route('/cart', methods=["GET", "POST"])
@login_required
def cart():
    if request.method == 'POST':
        search = request.form['search']
        with session_scope() as session:
            genre_list = session.query(Genre).all()
            filter_book = session.query(Book).filter(Book.title.ilike(f'%{search}%')).all()
            return render_template('genre_home.html', books_list=filter_book, title=search, genres=genre_list)
    cart_list = []
    res=0
    with session_scope() as session:
        cart_list_db = session.query(CartItem).filter_by(user_id=current_user.id).all()
        for item in cart_list_db:
            book = session.query(Book).filter_by(id=item.book_id).first()
            list_item = {
                'title': book.title,
                'author': book.author,
                'price': book.price,
                'count': item.count,
                'book_id':item.book_id,
                'price_count': round(book.price*item.count, 2)
            }
            cart_list.append(list_item)
        for i in cart_list:
            res += i['price']*i['count']
        genre_list = session.query(Genre).all()
        session.commit()
        return render_template('cart.html', genres=genre_list, books_list=cart_list, itog=round(res, 2))


@main_blueprint.route('/edit_cart/<action>/<id_book>')
@login_required
def edit_cart(action, id_book):
    match action:
        case '+':
            with session_scope() as session:
                cart_item = session.query(CartItem).filter(cast(CartItem.book_id, String) == id_book,
                                                           CartItem.user_id == current_user.id).first()
                cart_item.count += 1
                session.commit()
                return redirect(url_for('main.cart'))
        case '-':
            with session_scope() as session:
                cart_item = session.query(CartItem).filter(cast(CartItem.book_id, String) == id_book,
                                                           CartItem.user_id == current_user.id).first()
                if cart_item.count == 1:
                    session.delete(cart_item)
                    session.commit()
                    return redirect(url_for('main.cart'))
                cart_item.count -= 1
                session.commit()
                return redirect(url_for('main.cart'))
        case 'del':
            with session_scope() as session:
                cart_item = session.query(CartItem).filter(cast(CartItem.book_id, String) == id_book,
                                                           CartItem.user_id == current_user.id).first()
                session.delete(cart_item)
                session.commit()
                return redirect(url_for('main.cart'))


@main_blueprint.route('/type_address/<itog>', methods=["GET", "POST"])
@login_required
def type_address(itog):
    form=OrderForm()
    form_address=AddressForm()
    if request.method == "POST":
        if form.type_address.data == 'door':
            return render_template('form_address.html', form=form_address, itog=itog)
        date_today = date.today()
        order_new = Order(date=date_today, user_id=current_user.id, address=form.type_address.data, price=itog)
        with session_scope() as session:
            session.add(order_new)
            session.commit()
            id_order = order_new.id
            cart_list_db = session.query(CartItem).filter_by(user_id=current_user.id).all()
            for item in cart_list_db:
                book = session.query(Book).filter_by(id=item.book_id).first()
                orderitem_new = OrderItem(book_id=item.book_id, order_id=id_order, count=item.count, price=book.price)
                session.add(orderitem_new)
                session.commit()
            session.query(CartItem).delete()
            return redirect(url_for('main.orders_page'))
    return render_template('form_order.html', summa=itog, user=current_user, form=form)


@main_blueprint.route('/order/<itog>', methods=["GET", "POST"])
@login_required
def order(itog):
    form=AddressForm()
    if form.validate_on_submit():
        date_today = date.today()
        order_new = Order(date=date_today, user_id=current_user.id, address=form.address.data, price=itog)
        with session_scope() as session:
            session.add(order_new)
            session.commit()
            id_order = order_new.id
            cart_list_db = session.query(CartItem).filter_by(user_id=current_user.id).all()
            for item in cart_list_db:
                book = session.query(Book).filter_by(id=item.book_id).first()
                orderitem_new = OrderItem(book_id=item.book_id, order_id=id_order, count=item.count, price=book.price)
                session.add(orderitem_new)
                session.commit()
            session.query(CartItem).delete()
            return redirect(url_for('main.orders_page'))
    elif form.errors:
        flash(form.errors, category='danger')
    return render_template('form_address.html', form=form)


@main_blueprint.route('/orders_page', methods=["GET", "POST"])
@login_required
def orders_page():
    if request.method == 'POST':
        search = request.form['search']
        with session_scope() as session:
            genre_list = session.query(Genre).all()
            filter_book = session.query(Book).filter(Book.title.ilike(f'%{search}%')).all()
            return render_template('genre_home.html', books_list=filter_book, title=search, genres=genre_list)
    with session_scope() as session:
        genre_list = session.query(Genre).all()
        list_order = session.query(Order).filter_by(user_id=current_user.id).all()
        return render_template('orders_list.html', genres=genre_list, books_list=list_order)