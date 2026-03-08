#!/bin/sh
set -e
# Создаём таблицы один раз (избегаем гонки при нескольких воркерах gunicorn)
python -c "
from app import create_app, db
from app import models  # noqa: F401
app = create_app()
with app.app_context():
    db.create_all()
"
exec gunicorn --bind 0.0.0.0:5000 --workers 2 app:app
