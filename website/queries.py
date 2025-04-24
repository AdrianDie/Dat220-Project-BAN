import sqlite3
import datetime

# Definerer stien til databasen én gang for enkel gjenbruk
DATABASE_PATH = "instance/database.db"

def new_score(user_id, score):
    # Bruker DATABASE_PATH
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # created_at settes automatisk av databasen (DEFAULT CURRENT_TIMESTAMP),
    # så vi trenger ikke sende den med.
    # Hvis du *absolutt* vil sette den fra Python:
    # created_at = datetime.datetime.now()
    # cursor.execute("""INSERT INTO high_scores(score, user_id, created_at)
    #                VALUES(?, ?, ?)""", (score, user_id, created_at))
    # Men det er enklere å la DB gjøre det:
    cursor.execute("""INSERT INTO high_scores(score, user_id)
                   VALUES(?, ?)""", (score, user_id))

    conn.commit()
    conn.close()

def get_best_scores(limit):
    # Bruker DATABASE_PATH
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Bruker korrekt tabellnavn 'user'
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
    # Bruker DATABASE_PATH
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Bruker korrekt tabellnavn 'user'
    cursor.execute("""
    SELECT id, username, user_role FROM user WHERE username LIKE ?
    """, (name,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_role(user_id):
    # Bruker DATABASE_PATH
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Bruker korrekt tabellnavn 'user'
    cursor.execute("""
    SELECT user_role FROM user WHERE id = ?
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()
    return rows[0][0] if rows else ""

def remove_user(user_id):
    # Bruker DATABASE_PATH
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Bruker korrekt tabellnavn 'user'
    # Husk at ON DELETE CASCADE i create.py vil håndtere sletting av relaterte data (notes, scores, comments etc.)
    cursor.execute("""
    DELETE FROM user WHERE id = ?
    """, (user_id,))

    conn.commit()
    conn.close()

def get_notes(user_id):
    # Bruker DATABASE_PATH
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Bruker korrekt tabellnavn 'note'
    cursor.execute("""
    SELECT id, data, created_at FROM note WHERE user_id = ? ORDER BY created_at DESC
    """, (user_id,)) # Lagt til ORDER BY

    rows = cursor.fetchall()
    conn.close()

    return rows

def new_note(data, user_id):
    # Bruker DATABASE_PATH
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Lar databasen sette created_at
    cursor.execute("""INSERT INTO note(data, user_id)
                   VALUES(?, ?)""", (data, user_id))
    conn.commit()
    conn.close()


# ---------- REVIDERTE KOMMENTAR-FUNKSJONER ----------

def get_comments_for_page(page):
    comments_data = [] # Returner tom liste hvis feil eller ingen kommentarer
    try:
        # Bruker korrekt DATABASE_PATH
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        # Bruker korrekte tabellnavn 'Comments' og 'user'
        # Bruker korrekte kolonnenavn 'Comments.content' og 'user.username'
        # Henter også 'created_at' for sortering
        cursor.execute("""
            SELECT Comments.content, user.username, Comments.created_at
            FROM Comments
            JOIN user ON Comments.user_id = user.id
            WHERE Comments.page = ?
            ORDER BY Comments.created_at DESC
        """, (page,))
        # Formaterer resultatet til en liste av dictionaries for enkel bruk i malen
        comments_data = [{"content": row[0], "username": row[1], "created_at": row[2]} for row in cursor.fetchall()]
        conn.close()
    except sqlite3.Error as e:
        print(f"Database error in get_comments_for_page: {e}")
        # Vurder å logge feilen mer formelt her
    return comments_data

def insert_comment(user_id, page, content):
    try:
        # Bruker korrekt DATABASE_PATH
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        # Bruker korrekt tabellnavn 'Comments' og kolonner 'user_id', 'page', 'content'
        # Lar databasen sette 'id' og 'created_at' automatisk
        cursor.execute("""
            INSERT INTO Comments (user_id, page, content)
            VALUES (?, ?, ?)
        """, (user_id, page, content))
        conn.commit()
        conn.close()
        return True # Returnerer True ved suksess
    except sqlite3.Error as e:
        print(f"Database error in insert_comment: {e}")
        # Vurder å logge feilen mer formelt her
        conn.rollback() # Ruller tilbake endringer ved feil
        conn.close()
        return False # Returnerer False ved feil
# ---------- SLUTT PÅ REVIDERTE KOMMENTAR-FUNKSJONER ----------

# ---------- FUNKSJON FOR TILBAKEMELDING ----------

def add_feedback(user_id, message):
    """Lagrer en ny tilbakemelding i feedback-tabellen."""
    try:
        # Bruker den globale DATABASE_PATH
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        # Bruker korrekt tabellnavn 'feedback' og kolonner 'user_id', 'message'
        # Lar databasen sette 'id' og 'submitted_at' automatisk
        cursor.execute("""
            INSERT INTO feedback (user_id, message)
            VALUES (?, ?)
        """, (user_id, message))
        conn.commit()
        conn.close()
        return True # Returnerer True ved suksess
    except sqlite3.Error as e:
        print(f"Database error in add_feedback: {e}")
        # Vurder å logge feilen mer formelt her
        if conn: # Sjekk om tilkoblingen ble etablert før vi prøver å rulle tilbake/lukke
            conn.rollback() # Ruller tilbake endringer ved feil
            conn.close()
        return False # Returnerer False ved feil

# ---------- SLUTT PÅ FUNKSJON FOR TILBAKEMELDING ----------

def get_all_feedback():
    """Henter alle tilbakemeldinger med tilhørende brukernavn."""
    feedback_data = [] # Returner tom liste hvis feil eller ingen feedback
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        # Henter feedback-id, melding, tidspunkt og brukernavn ved å joine tabellene
        cursor.execute("""
            SELECT feedback.id, feedback.message, feedback.submitted_at, user.username
            FROM feedback
            JOIN user ON feedback.user_id = user.id
            ORDER BY feedback.submitted_at DESC -- Viser de nyeste først
        """)
        # Formaterer resultatet til en liste av dictionaries for enkel bruk i malen
        feedback_data = [
            {"id": row[0], "message": row[1], "submitted_at": row[2], "username": row[3]}
            for row in cursor.fetchall()
        ]
        conn.close()
    except sqlite3.Error as e:
        print(f"Database error in get_all_feedback: {e}")
        # Vurder logging
    return feedback_data

# ---------- SLUTT PÅ NY FUNKSJON ----------