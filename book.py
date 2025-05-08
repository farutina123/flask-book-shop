from flask import Blueprint, flash, redirect, url_for, render_template, request, Response
from flask_login import login_required, current_user
from db.database import session_scope
from db.models import Book, Genre, Review, CartItem
from sqlalchemy import cast, String
from forms.review_form import ReviewForm



book_blueprint = Blueprint('book', __name__, url_prefix='/')


@book_blueprint.route('/book_page/<id_book>', methods=["GET", "POST"])
def book_page(id_book):
    if request.method == 'POST':
        search = request.form['search']
        with session_scope() as session:
            genre_list = session.query(Genre).all()
            filter_book = session.query(Book).filter(Book.title.ilike(f'%{search}%')).all()
            return render_template('genre/genre_not_log.html', books_list=filter_book, title=search, genres=genre_list)
    with session_scope() as session:
        genre_list = session.query(Genre).all()
        book = session.query(Book).filter(cast(Book.id, String) == id_book).first()
        if book:
            return render_template('book/book_page.html', book=book, genres=genre_list)
        return Response(
        status=404,
    )

@book_blueprint.route('/book_page_review/<id_book>', methods=["GET", "POST"])
@login_required
def book_page_review(id_book):
    if request.method == 'POST':
        search = request.form['search']
        with session_scope() as session:
            genre_list = session.query(Genre).all()
            filter_book = session.query(Book).filter(Book.title.ilike(f'%{search}%')).all()
            return render_template('genre/genre_home.html', books_list=filter_book, title=search, genres=genre_list)
    with session_scope() as session:
        genre_list = session.query(Genre).all()
        book = session.query(Book).filter(cast(Book.id, String) == id_book).first()
        if not book:
            return Response(
                status=404,
            )
        book_reviews_list = session.query(Review).filter_by(book_id=id_book).all()
        if book_reviews_list:
            return render_template("book/book_with_review.html", genres=genre_list, book=book,
                                   list_reviews=book_reviews_list)
        return render_template('book/book_page_review.html', book=book, genres=genre_list)


@book_blueprint.route('/review/<id_book>', methods=["GET", "POST"])
@login_required
def review_info(id_book):
    form = ReviewForm()
    if not request.method == 'POST':
        return render_template('form/review.html', form=form, book=id_book)
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
        return redirect(url_for('book.book_page_review', id_book=book.id))


@book_blueprint.route('/buy/<id_book>/<path>')
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
        return redirect(url_for('book.book_page_review', id_book=id_book))
    flash('книга добавлена в корзину', 'info')
    return redirect(url_for('main.main_route', id_book=id_book))


@book_blueprint.route('/buy_genre/<id_book>/<title>')
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

