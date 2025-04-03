import sqlite3
import datetime

def new_score(user_id, score):
    conn = sqlite3.connect("instance/database.db")
    cursor = conn.cursor()
    
    created_at = datetime.datetime.now()

    cursor.execute("""INSERT INTO high_scores(score, user_id, created_at) 
                   VALUES(?, ?, ?)""", (score, user_id, created_at))
    conn.commit()
    conn.close()

def get_best_scores(limit):
    conn = sqlite3.connect("instance/database.db")
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT user.username, high_scores.score
    FROM high_scores
    JOIN user ON high_scores.user_id = user.id
    ORDER BY high_scores.score DESC
    LIMIT ?""", (limit,))

    rows = cursor.fetchall()
    conn.close()
    return rows

def get_users(name):
    conn = sqlite3.connect("instance/database.db")
    cursor = conn.cursor()

    cursor.execute("""
SELECT id, username, user_role FROM user WHERE username LIKE ?
    """, (name,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_role(user_id):
    conn = sqlite3.connect("instance/database.db")
    cursor = conn.cursor()

    cursor.execute("""
SELECT user_role FROM user WHERE id = ?
    """, (user_id,))
    
    rows = cursor.fetchall()
    conn.close()
    return rows[0][0] if rows else "" 

def remove_user(user_id):
    conn = sqlite3.connect("instance/database.db")
    cursor = conn.cursor()

    cursor.execute("""
DELETE FROM user WHERE id = ?
    """, (user_id,))

    conn.commit()
    conn.close()

def get_notes(user_id):
    conn = sqlite3.connect("instance/database.db")
    cursor = conn.cursor()

    cursor.execute("""
SELECT id, data, created_at FROM note WHERE user_id = ?
    """, (user_id,))
    
    rows = cursor.fetchall()
    conn.close()

    return rows

def new_note(data, user_id):
    conn = sqlite3.connect("instance/database.db")
    cursor = conn.cursor()
    
    created_at = datetime.datetime.now()

    cursor.execute("""INSERT INTO note(data, user_id, created_at) 
                   VALUES(?, ?, ?)""", (data, user_id, created_at))
    conn.commit()
    conn.close()
