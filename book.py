from flask import Blueprint, flash, redirect, url_for, render_template, request, Response
from flask_login import login_required, current_user
from db.database import session_scope
from db.models import Book, Genre, Review, CartItem, User
from sqlalchemy import cast, String
from forms.review_form import ReviewForm

book_photo = 'https://content.img-gorod.ru/pim/products/images/f1/0e/018fa2d6-0649-7070-ab14-c5b66029f10e.jpg?width=0&height=1200&fit=bounds'
book_blueprint = Blueprint('book', __name__, url_prefix='/')


@book_blueprint.route('/book_page/<book_id>')
def book_page(book_id):
    with session_scope() as session:
        genre_list = session.query(Genre).all()
        book = session.query(Book).filter(cast(Book.id, String) == book_id).first()
        if not book:
            return Response(
                status=404,
            )
        book_reviews = session.query(Review).filter_by(book_id=book_id).all()
        if not book_reviews:
            return render_template('book/book_page.html', book=book, genres=genre_list, photo=book_photo)
        book_reviews_list = []
        for item in book_reviews:
            user = session.query(User).filter_by(id=item.user_id).first()
            list_item = {
                'username': user.username,
                'rating': item.rating,
                'review_book': item.review_book,
            }
            book_reviews_list.append(list_item)
        return render_template('book/book_with_review_not_log.html', photo=book_photo, genres=genre_list, book=book,
                               list_reviews=book_reviews_list)


@book_blueprint.route('/book_page_review/<book_id>')
@login_required
def book_page_review(book_id):
    with session_scope() as session:
        genre_list = session.query(Genre).all()
        book = session.query(Book).filter(cast(Book.id, String) == book_id).first()
        if not book:
            return Response(
                status=404,
            )
        book_reviews = session.query(Review).filter_by(book_id=book_id).all()
        if book_reviews:
            book_reviews_list = []
            for item in book_reviews:
                user = session.query(User).filter_by(id=item.user_id).first()
                list_item = {
                    'username': user.username,
                    'rating': item.rating,
                    'review_book': item.review_book,
                }
                book_reviews_list.append(list_item)
            return render_template('book/book_with_review.html', photo=book_photo, genres=genre_list, book=book,
                                   list_reviews=book_reviews_list)
        return render_template('book/book_page_review.html', photo=book_photo, book=book, genres=genre_list)


@book_blueprint.route('/review/<book_id>', methods=['GET', 'POST'])
@login_required
def review_info(book_id):
    form = ReviewForm()
    if not request.method == 'POST':
        return render_template('form/review.html', form=form, book=book_id)
    review = Review(review_book=form.review.data, book_id=book_id, user_id=current_user.id,
                    rating=float(form.rating.data))
    with session_scope() as session:
        session.add(review)
    with session_scope() as session:
        book_reviews_list = session.query(Review).filter_by(book_id=book_id).all()
        res_sum = 0
        for i in book_reviews_list:
            res_sum += i.rating
        res = res_sum / len(book_reviews_list)
        session.commit()
        book = session.query(Book).filter(cast(Book.id, String) == book_id).first()
        book.rating = round(res, 2)
        session.commit()
        return redirect(url_for('book.book_page_review', photo=book_photo, book_id=book.id))


@book_blueprint.route('/buy/<book_id>/<path>')
@login_required
def buy(book_id, path):
    with session_scope() as session:
        test_book = session.query(CartItem).filter(cast(CartItem.book_id, String) == book_id,
                                                   CartItem.user_id == current_user.id).first()
        if test_book:
            test_book.count += 1
        else:
            cart_item = CartItem(book_id=book_id, user_id=current_user.id)
            session.add(cart_item)
            session.commit()
    if path == 'book_page_review':
        flash('книга добавлена в корзину', 'info')
        return redirect(url_for('book.book_page_review', book_id=book_id))
    flash('книга добавлена в корзину', 'info')
    return redirect(url_for('main.main_route', book_id=book_id))


@book_blueprint.route('/buy_genre/<book_id>/<title>')
@login_required
def buy_genre(book_id, title):
    with session_scope() as session:
        test_book = session.query(CartItem).filter(cast(CartItem.book_id, String) == book_id,
                                                   CartItem.user_id == current_user.id).first()
        if test_book:
            test_book.count += 1
        else:
            cart_item = CartItem(book_id=book_id, user_id=current_user.id)
            session.add(cart_item)
            session.commit()
    flash('книга добавлена в корзину', 'info')
    return redirect(url_for('main.group_of_genre_home', title_genre=title))
