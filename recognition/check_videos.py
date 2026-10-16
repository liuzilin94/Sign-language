from ui_plus import app
from backend.models import db, Word

with app.app_context():
    words = Word.query.limit(10).all()
    for w in words:
        print(f'ID:{w.id} word:{w.word} backend_id:{w.backend_id} video:{w.demo_video_url}')
