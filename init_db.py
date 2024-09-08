# init_db.py
from main import app, db  # Asegúrate de que 'app' y 'db' se importan correctamente

with app.app_context():
    db.create_all()
    print("Database tables created!")
