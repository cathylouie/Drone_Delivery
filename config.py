import os

# Config file, put all your keys and passwords and whatnot in here
DB_URI = os.environ.get("DATABASE_URL", "sqlite:///DuckieStore_app.db")
SECRET_KEY = "TwinkleTwinkleLittleStars"
