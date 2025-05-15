from flask import Blueprint, flash, redirect, url_for, render_template, request, Response
from flask_login import login_required, current_user
from db.database import session_scope
from db.models import Book, Genre, CartItem, OrderItem, Order
from sqlalchemy import cast, String
from datetime import date
from forms.address_form import AddressForm
from forms.order_form import OrderForm
from book import book_photo

cart_order_blueprint = Blueprint('cart_order', __name__, url_prefix='/')


def itog_summa():
    cart_list = []
    res = 0
    with session_scope() as session:
        cart_list_db = session.query(CartItem).filter_by(user_id=current_user.id).all()
        book_ids = [str(item.book_id) for item in cart_list_db]
        books = {str(book.id): book for book in session.query(Book).filter(Book.id.in_(book_ids)).all()}
        for item in cart_list_db:
            book = books[f'{item.book_id}']
            list_item = {
                'title': book.title,
                'author': book.author,
                'price': book.price,
                'count': item.count,
                'book_id': item.book_id,
                'price_count': round(book.price * item.count, 2)
            }
            cart_list.append(list_item)
        for i in cart_list:
            res += i['price'] * i['count']
        summa = round(res, 2)
    return summa, cart_list


@cart_order_blueprint.route('/cart')
@login_required
def cart():
    res, cart_list = itog_summa()
    with session_scope() as session:
        genre_list = session.query(Genre).all()
        session.commit()
        return render_template('cart_and_order/cart.html', genres=genre_list, books_list=cart_list, itog=res)


@cart_order_blueprint.route('/edit_cart_plus/<book_id>')
@login_required
def edit_cart_plus(book_id):
    with session_scope() as session:
        cart_item = session.query(CartItem).filter(cast(CartItem.book_id, String) == book_id,
                                                   CartItem.user_id == current_user.id).first()
        cart_item.count += 1
        session.commit()
        return redirect(url_for('cart_order.cart'))


@cart_order_blueprint.route('/edit_cart_minus/<book_id>')
@login_required
def edit_cart_minus(book_id):
    with session_scope() as session:
        cart_item = session.query(CartItem).filter(cast(CartItem.book_id, String) == book_id,
                                                   CartItem.user_id == current_user.id).first()
        if cart_item.count == 1:
            session.delete(cart_item)
            session.commit()
            return redirect(url_for('cart_order.cart'))
        cart_item.count -= 1
        session.commit()
        return redirect(url_for('cart_order.cart'))


@cart_order_blueprint.route('/edit_cart_del/<book_id>')
@login_required
def edit_cart_del(book_id):
    with session_scope() as session:
        cart_item = session.query(CartItem).filter(cast(CartItem.book_id, String) == book_id,
                                                   CartItem.user_id == current_user.id).first()
        session.delete(cart_item)
        session.commit()
        return redirect(url_for('cart_order.cart'))


@cart_order_blueprint.route('/type_address_get')
@login_required
def type_address_get():
    form = OrderForm()
    res = itog_summa()[0]
    with session_scope() as session:
        list_cart = session.query(CartItem).first()
    if list_cart:
        return render_template('form/form_order.html', summa=res, user=current_user, form=form)
    flash("корзина пуста", 'danger')
    return redirect(url_for('cart_order.cart'))


@cart_order_blueprint.route('/type_address', methods=["GET", "POST"])
@login_required
def type_address():
    form = OrderForm()
    form_address = AddressForm()
    res = itog_summa()[0]
    if not request.method == "POST":
        return redirect(url_for('cart_order.type_address_get'))
    if form.type_address.data == 'door':
        return render_template('form/form_address.html', form=form_address)
    date_today = date.today()
    order_new = Order(date=date_today, user_id=current_user.id, address=form.type_address.data, price=res)
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
        return redirect(url_for('cart_order.orders_page'))


@cart_order_blueprint.route('/order', methods=["GET", "POST"])
@login_required
def order():
    form = AddressForm()
    res = itog_summa()[0]
    if not form.validate_on_submit():
        if form.errors:
            flash(form.errors, category='danger')
        return render_template('form/form_address.html', form=form)
    date_today = date.today()
    order_new = Order(date=date_today, user_id=current_user.id, address=form.address.data, price=res)
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
        return redirect(url_for('cart_order.orders_page'))


@cart_order_blueprint.route('/orders_page')
@login_required
def orders_page():
    with session_scope() as session:
        genre_list = session.query(Genre).all()
        list_order = session.query(Order).filter_by(user_id=current_user.id).all()
        return render_template('cart_and_order/orders_list.html', genres=genre_list, books_list=list_order)


@cart_order_blueprint.route('/order_page/<id_order>')
@login_required
def order_page(id_order):
    order_list = []
    res = 0
    with session_scope() as session:
        order = session.query(Order).filter(Order.id == id_order, Order.user_id == current_user.id).first()
        if not order:
            return Response(
                status=404,
            )
        orderitem_list = session.query(OrderItem).filter_by(order_id=id_order).all()
        status = order.status
        address = order.address
        book_ids = [str(item.book_id) for item in orderitem_list]
        books = {str(book.id): book for book in session.query(Book).filter(Book.id.in_(book_ids)).all()}
        for item in orderitem_list:
            book = books[f'{item.book_id}']
            list_item = {
                'title': book.title,
                'author': book.author,
                'price': book.price,
                'count': item.count,
                'price_count': round(book.price * item.count, 2),
                'book_id': item.book_id
            }
            order_list.append(list_item)
        for i in order_list:
            res += i['price'] * i['count']
        genre_list = session.query(Genre).all()
        return render_template('cart_and_order/order.html', photo=book_photo, genres=genre_list,
                               books_list=order_list, id=id_order, status=status, itog=round(res, 2),
                               address=address, user=current_user.username, date=order.date)
