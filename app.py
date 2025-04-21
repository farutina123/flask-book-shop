from flask import Flask
from config import settings
from db.database import init_db

app = Flask(__name__)
app.config['SECRET_KEY'] = settings.SECRET_KEY

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5466)