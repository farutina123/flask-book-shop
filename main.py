from flask import Blueprint, render_template, request
from flask_login import login_required
from db.database import session_scope
from db.models import Book, Genre
import json
from sqlalchemy.sql.expression import func
from book import book_photo


main_blueprint = Blueprint('main', __name__, url_prefix='/')


def get_random_books(session, count=3):
    random_books = session.query(Book).order_by(func.random()).limit(count).all()
    return random_books


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
        rand_books = get_random_books(session, count=3)
        return render_template('genre/not_log.html', photo=book_photo, genres=genre_list, top=rand_books)


@main_blueprint.route('/main', methods=["GET", "POST"])
@login_required
def main_route():
    if request.method == 'POST':
        search = request.form['search']
        with session_scope() as session:
            genre_list = session.query(Genre).all()
            filter_book = session.query(Book).filter(Book.title.ilike(f'%{search}%')).all()
            return render_template('genre/genre_home.html', photo=book_photo, books_list=filter_book, title=search, genres=genre_list)
    with session_scope() as session:
        genre_list = session.query(Genre).all()
        rand_books = get_random_books(session, count=3)
        return render_template('genre/home.html', photo=book_photo, genres=genre_list, top=rand_books)


@main_blueprint.route('/genre_log/<title_genre>', methods=["GET", "POST"])
@login_required
def group_of_genre_home(title_genre):
    if request.method == 'POST':
        search = request.form['search']
        with session_scope() as session:
            genre_list = session.query(Genre).all()
            filter_book = session.query(Book).filter(Book.title.ilike(f'%{search}%')).all()
            return render_template('genre/genre_home.html', photo=book_photo, books_list=filter_book, title=search, genres=genre_list)
    with session_scope() as session:
        books_list = session.query(Book).filter_by(genre=title_genre)
        genre_list = session.query(Genre)
    return render_template('genre/genre_home.html', photo=book_photo, genres=genre_list, title=title_genre, books_list=books_list)


@main_blueprint.route('/genre/<title_genre>')
def group_of_genre(title_genre):
    with session_scope() as session:
        books_list = session.query(Book).filter_by(genre=title_genre)
        genre_list = session.query(Genre)
    return render_template('genre/genre_not_log.html', photo=book_photo, genres=genre_list, title=title_genre, books_list=books_list)


@main_blueprint.route('/search', methods=["GET", "POST"])
def search():
    if not request.method == 'POST':
        with session_scope() as session:
            genre_list = session.query(Genre)
            rand_books = get_random_books(session, count=3)
            return render_template('genre/not_log.html', photo=book_photo, genres=genre_list, top=rand_books)
    search = request.form['search']
    with session_scope() as session:
        genre_list = session.query(Genre).all()
        filter_book = session.query(Book).filter(Book.title.ilike(f'%{search}%')).all()
        return render_template('genre/genre_not_log.html', photo=book_photo, books_list=filter_book, title=search,
                               genres=genre_list)