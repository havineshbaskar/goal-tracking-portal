import os

class Config:
    SECRET_KEY = 'goaltrackingsecretkey'
    DATABASE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database.db')