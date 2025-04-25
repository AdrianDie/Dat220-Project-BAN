import sqlite3
import secrets

from werkzeug.security import generate_password_hash, check_password_hash

DATABASE_PATH = "instance/database.db"

def get_files(user_id):
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT id, filename, uploaded_at 
    FROM Files 
    WHERE user_id = ? 
    ORDER BY uploaded_at DESC
    """, (user_id,))
    
    files = cursor.fetchall()
    conn.close()
    
    return [dict(file) for file in files]

def insert_file(user_id, filename):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT INTO Files (user_id, filename)
    VALUES (?, ?)
    """, (user_id, filename))
    
    conn.commit()
    conn.close()
    
    return True

def check_username_exists(username):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM user WHERE username = ?", (username,))
    count = cursor.fetchone()[0]
    
    conn.close()
    return count > 0

def create_user(username, password):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM user")
    user_count = cursor.fetchone()[0]
    role = "admin" if user_count == 0 else "regular"
    
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    salt = secrets.token_hex(16)
    
    cursor.execute("""
    INSERT INTO user (username, password, salt, user_role)
    VALUES (?, ?, ?, ?)
    """, (username, hashed_password, salt, role))
    
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return user_id

def verify_password(username, password):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, password FROM user WHERE username = ?", (username,))
    result = cursor.fetchone()
    
    conn.close()
    
    if not result:
        return None
    
    user_id, stored_password = result
    
    if check_password_hash(stored_password, password):
        return user_id
    
    return None

def change_user_password(user_id, new_password):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
    
    cursor.execute("UPDATE user SET password = ? WHERE id = ?", 
                  (hashed_password, user_id))
    
    conn.commit()
    conn.close()
    
    return True

def create_session(user_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    token = secrets.token_hex(32)
    
    cursor.execute("""
    INSERT INTO sessions (user_id, token)
    VALUES (?, ?)
    """, (user_id, token))
    
    conn.commit()
    conn.close()
    
    return token

def validate_session(token):
    if not token:
        return None
        
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT user_id FROM sessions WHERE token = ?
    """, (token,))
    
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else None

def delete_session(token):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
    DELETE FROM sessions WHERE token = ?
    """, (token,))
    
    conn.commit()
    conn.close()

def get_user_by_id(user_id):
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT id, username, user_role, profile_description
    FROM user WHERE id = ?
    """, (user_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return None
    
    return dict(result)

def new_score(user_id, score):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""INSERT INTO high_scores(score, user_id)
                   VALUES(?, ?)""", (score, user_id))

    conn.commit()
    conn.close()

def get_best_scores(limit):
    conn = sqlite3.connect(DATABASE_PATH)
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
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, username, user_role FROM user WHERE username LIKE ?
    """, (name,))
    rows = cursor.fetchall()
    conn.close()
    
    return rows

def get_role(user_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT user_role FROM user WHERE id = ?
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()
    return rows[0][0] if rows else ""

def remove_user(user_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    #we dont really care about storing tokens from deleted user, so it can go away too
    cursor.execute("""
    DELETE FROM sessions WHERE user_id = ?
    """, (user_id,))

    cursor.execute("""
    DELETE FROM user WHERE id = ?
    """, (user_id,))

    conn.commit()
    conn.close()

def get_notes(user_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, data, created_at FROM note WHERE user_id = ? ORDER BY created_at DESC
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()

    return rows

def update_note_content(note_id, user_id, new_content):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT COUNT(*) FROM note WHERE id = ? AND user_id = ?
    """, (note_id, user_id))
    
    count = cursor.fetchone()[0]

    if count == 0:
        conn.close()
        return False

    cursor.execute("""
    UPDATE note 
    SET data = ?, created_at = CURRENT_TIMESTAMP
    WHERE id = ?
    """, (new_content, note_id))
    
    conn.commit()
    conn.close()
    return True

def new_note(data, user_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""INSERT INTO note(data, user_id)
    VALUES(?, ?)""", (data, user_id))
    conn.commit()
    conn.close()

def remove_note(note_id, user_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT COUNT(*) FROM note WHERE id = ? AND user_id = ?
    """, (note_id, user_id))
    
    count = cursor.fetchone()[0]

    if count == 0:
        conn.close()
        return False
    
    cursor.execute("""
    DELETE FROM note WHERE id = ? AND user_id = ?               
    """, (note_id, user_id))

    conn.commit()
    conn.close()
    return True

def get_comments_for_page(page):
    comments_data = []
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Comments.content, user.username, Comments.created_at
            FROM Comments
            JOIN user ON Comments.user_id = user.id
            WHERE Comments.page = ?
            ORDER BY Comments.created_at DESC
        """, (page,))
        comments_data = [{"content": row[0], "username": row[1], "created_at": row[2]} for row in cursor.fetchall()]
        conn.close()
    except sqlite3.Error as e:
        print(f"Database error in get_comments_for_page: {e}")
    return comments_data

def insert_comment(user_id, page, content):
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Comments (user_id, page, content)
            VALUES (?, ?, ?)
        """, (user_id, page, content))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Database error in insert_comment: {e}")
        conn.rollback()
        conn.close()
        return False

def get_chat(limit):
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
        
    cursor.execute("""
    SELECT user.username, Live_chat.message_text, Live_chat.timestamp
    FROM Live_chat
    JOIN user ON Live_chat.user_id = user.id
    ORDER BY Live_chat.timestamp DESC
    LIMIT ?
    """, (limit,))
        
    rows = cursor.fetchall()
    conn.close()

    return reversed(rows)

def insert_chat(user_id, content):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
                
    cursor.execute("""
    INSERT INTO Live_chat (user_id, message_text)
    VALUES (?, ?)
    """, (user_id, content,))
        
    conn.commit()
    conn.close()

def get_biography(user_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
        
    cursor.execute("""
    SELECT profile_description 
    FROM user
    WHERE id = ?
    """, (user_id,))
        
    result = cursor.fetchone()
    conn.close()
        
    return result[0] if result else ""

def set_biography(user_id, content):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
    UPDATE user 
    SET profile_description = ?, last_updated = CURRENT_TIMESTAMP 
    WHERE id = ?
    """, (content, user_id))
    
    conn.commit()
    conn.close()

def clear_sessions_except_current(user_id, current_token):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
    DELETE FROM sessions WHERE user_id = ? AND token != ?
    """, (user_id, current_token))
    
    counter = cursor.rowcount
    conn.commit()
    conn.close()

    return counter

def get_session_count(user_id):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT user_id, COUNT(*) AS session_count FROM sessions WHERE user_id = ? GROUP BY user_id
    """, (user_id,))
    
    count = cursor.fetchone()[1]
    conn.close()
    
    return count


def collect_public_information(username):
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT id, username, profile_description as biography, 
           last_updated as bio_updated, time_created
    FROM user
    WHERE username = ?
    """, (username,))
    
    user_data = cursor.fetchone()
    conn.close()
    
    if not user_data:
        return None
    
    return dict(user_data)

def add_feedback(user_id, message):
    """Lagrer en ny tilbakemelding i feedback-tabellen."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO feedback (user_id, message)
            VALUES (?, ?)
        """, (user_id, message))
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Database error in add_feedback: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

def get_all_feedback():
    """Henter alle tilbakemeldinger med tilhørende brukernavn."""
    feedback_data = []
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT feedback.id, feedback.message, feedback.submitted_at, user.username
            FROM feedback
            JOIN user ON feedback.user_id = user.id
            ORDER BY feedback.submitted_at DESC -- Viser de nyeste først
        """)
        feedback_data = [
            {"id": row[0], "message": row[1], "submitted_at": row[2], "username": row[3]}
            for row in cursor.fetchall()
        ]
        conn.close()
    except sqlite3.Error as e:
        print(f"Database error in get_all_feedback: {e}")
    return feedback_data
