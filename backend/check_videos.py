# -*- coding: utf-8 -*-
import sqlite3

db_path = r'e:\csl-recognition\recognition-deploy\backend\csl_recognition.db'
conn = sqlite3.connect(db_path)
conn.text_factory = str
cursor = conn.cursor()

cursor.execute("SELECT backend_id, word, demo_video_url FROM words WHERE demo_video_url IS NOT NULL")
words = cursor.fetchall()
conn.close()

with open(r'e:\csl-recognition\recognition-deploy\backend\video_check.txt', 'w', encoding='utf-8') as f:
    f.write("="*60 + "\n")
    f.write("All words with video URLs:\n")
    f.write("="*60 + "\n")
    for backend_id, word, url in words:
        f.write("[%s] %s -> %s\n" % (backend_id, word, url))

print("Done")
