from flask import Flask
from flask_login import LoginManager
from config import settings
from db.database import init_db
from main import main_blueprint
from users import user_blueprint
from book import book_blueprint
from cart_order import cart_order_blueprint, session_scope

from db.models import User

app = Flask(__name__)

app.config['SECRET_KEY'] = settings.SECRET_KEY

app.register_blueprint(main_blueprint)
app.register_blueprint(user_blueprint)
app.register_blueprint(book_blueprint)
app.register_blueprint(cart_order_blueprint)


login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    with session_scope() as session:
        user = session.query(User).get(user_id)
        if user:
            session.expunge(user)
        return user


if __name__ == "__main__":
    init_db()
    app.run(debug=settings.DEBUG, port=settings.APP_PORT)
