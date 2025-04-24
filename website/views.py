from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, send_from_directory, session # La til session for flash meldinger etc.
from flask_login import login_required, current_user
# Importerer funksjonene direkte fra queries
from .queries import get_comments_for_page, insert_comment, add_feedback, get_all_feedback # Endret fra website.queries til .queries for relativ import
from .models import User, HighScores, Note, Files, Comments # Lagt til Comments her også
from . import db
import json
import os

# Oppretter en Blueprint kalt 'views_bp'
views_bp = Blueprint('views_bp', __name__)

# Setter opp mappe for opplastede filer (bør ideelt sett konfigureres i app/__init__.py)
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads') # Pass på at 'uploads' mappen finnes i roten av prosjektet
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Sjekk om en fil har en gyldig utvidelse
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Ruter for filopplasting (uendret) ---
@views_bp.route('/files', methods=['GET', 'POST'])
@login_required
def files():
    if request.method == 'POST':
        return upload_file()

    user_files = Files.query.filter_by(user_id=current_user.id).all()
    return render_template("Files.html", user=current_user, files=user_files)

def upload_file():
    if 'file' not in request.files:
        flash('Ingen fil valgt', 'error')
        return redirect(url_for('views_bp.files'))

    file = request.files['file']

    if file.filename == '':
        flash('Ingen fil valgt', 'error')
        return redirect(url_for('views_bp.files'))

    if file and allowed_file(file.filename):
        filename = file.filename # Bør sikres (f.eks. werkzeug.utils.secure_filename)
        # Sjekk om uploads-mappen finnes, hvis ikke, lag den
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        try:
            file.save(filepath)
            new_file = Files(user_id=current_user.id, filename=filename)
            db.session.add(new_file)
            db.session.commit()
            flash(f'Fil {filename} lastet opp!', 'success')
        except Exception as e:
            db.session.rollback() # Rull tilbake db-endring hvis lagring feiler
            flash(f'Kunne ikke lagre filen: {e}', 'error')
            print(f"Error saving file: {e}") # Logg feilen

        return redirect(url_for('views_bp.files'))

    flash('Filtypen er ikke tillatt', 'error')
    return redirect(url_for('views_bp.files'))


@views_bp.route('/uploads/<path:filename>') # Bruk path: for å tillate undermapper evt.
@login_required # Vurder om denne skal være public eller kreve login
def uploaded_file(filename):
    # Sikkerhet: Aldri send_from_directory med en path som kommer direkte fra bruker uten validering/sikring
    # Her henter vi filnavn fra databasen, så det er tryggere, men vær obs.
    # Sjekk at filen tilhører brukeren eller er ment å være public?
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=False) # as_attachment=False viser bildet i nettleser

# --- Forside (uendret) ---
@views_bp.route('/')
def home():
    return render_template("Forside.html", user=current_user)

# ---------- REVIDERT MATTESPILL-RUTE ----------
# Kombinerer visning av spill og kommentarer i én rute
@views_bp.route('/mattespill') # Bruker den originale URLen
@login_required
def spill_mattespill(): # Gi funksjonen et beskrivende navn
    try:
        # Henter kommentarer for 'mattespill'-siden ved hjelp av queries-funksjonen
        page_identifier = 'mattespill' # Definer side-identifikator
        comments = get_comments_for_page(page_identifier)
    except Exception as e:
        flash("Kunne ikke laste kommentarer.", "error")
        print(f"Error fetching comments for {page_identifier}: {e}") # Logg feil
        comments = [] # Vis tomt kommentarfelt ved feil

    # Sender både brukerinfo og kommentarer til malen
    return render_template("Spill-mattespill.html", user=current_user, comments=comments, page_name=page_identifier)

# Fjerner den gamle, dupliserte ruten:
# @views_bp.route('/spill-mattespill', methods=['GET'])
# def spill_mattespill():
#     comments = get_comments_for_page('mattespill')
#     return render_template("Spill-mattespill.html", comments=comments)
# ---------- SLUTT PÅ REVIDERING AV MATTESPILL-RUTE ----------


# --- Snake (uendret) ---
@views_bp.route('/snake')
@login_required
def snake():
    return render_template("Spill-snake.html", user=current_user)

# --- Score håndtering (uendret) ---
@views_bp.route('/submit-score', methods=['POST'])
@login_required
def submit_score():
    data = request.get_json()
    score = data.get('score')

    if score is not None: # Bedre sjekk enn bare 'if score:' (hvis score er 0)
        try:
            new_score_obj = HighScores(score=int(score), user_id=current_user.id)
            db.session.add(new_score_obj)
            db.session.commit()
            return jsonify({"message": "Poengsum lagret"}), 200
        except Exception as e:
            db.session.rollback()
            print(f"Error saving score: {e}")
            return jsonify({"error": "Kunne ikke lagre poengsum"}), 500
    return jsonify({"error": "Ingen poengsum oppgitt"}), 400

@views_bp.route('/high-scores')
@login_required
def high_scores():
    try:
        # Bruker SQLAlchemy direkte her, som er bra!
        top_scores = db.session.query(HighScores).join(User).order_by(HighScores.score.desc()).limit(3).all()
        scores_data = [{"username": score.user.username, "score": score.score} for score in top_scores]
        return jsonify(scores_data)
    except Exception as e:
        print(f"Error fetching high scores: {e}")
        return jsonify({"error": "Kunne ikke hente high scores"}), 500


# --- Brukeradmin (uendret) ---
@views_bp.route('/oversikt-brukere')
@login_required
def brukeroversikt():
    if current_user.user_role == 'admin':
        search_query = request.args.get('search', '')
        if search_query:
            users = User.query.filter(User.username.ilike(f'%{search_query}%')).all()
        else:
            users = User.query.all()
        return render_template('Oversikt-brukere.html', user=current_user, users=users)
    else:
        flash('Du har ikke tilgang til denne siden.', category='error')
        return redirect(url_for('views_bp.home'))

@views_bp.route('/delete-user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.user_role == 'admin':
        user_to_delete = User.query.get_or_404(user_id)
        # Ekstra sjekk: Ikke la admin slette seg selv via denne ruten
        if user_to_delete.id == current_user.id:
             flash('Du kan ikke slette din egen konto her.', category='error')
             return redirect(url_for('views_bp.brukeroversikt'))

        # Sjekker rollen før sletting (selv om DB cascade gjør jobben, kan være greit å ha logikk her)
        if user_to_delete.user_role != 'admin': # Eller spesifikt 'regular' hvis det er den eneste andre rollen
            try:
                db.session.delete(user_to_delete)
                db.session.commit()
                flash(f'Bruker {user_to_delete.username} slettet', category='success')
            except Exception as e:
                 db.session.rollback()
                 flash(f'Kunne ikke slette bruker: {e}', category='error')
                 print(f"Error deleting user: {e}")
        else:
            flash('Kan ikke slette administrator-kontoer.', category='error')
    else:
        flash('Ingen tilgang til å slette brukere.', category='error')
    return redirect(url_for('views_bp.brukeroversikt'))

# --- Andre spill (uendret) ---
@views_bp.route('/sprettball')
@login_required
def sprettballen():
    return render_template("Spill-sprettball.html", user=current_user)

@views_bp.route('/bildegate')
@login_required
def bilde_gate():
    return render_template("Spill-bildegater.html", user=current_user)

@views_bp.route('/oversikt-spill')
@login_required
def spillside():
    return render_template("Oversikt-spill.html", user=current_user)

# --- Notater (uendret) ---
@views_bp.route('/notes', methods=['GET'])
@login_required
def notes():
    user_notes = Note.query.filter_by(user_id=current_user.id).order_by(Note.created_at.desc()).all() # Lagt til sortering
    return render_template("Notes.html", user=current_user, notes=user_notes)

@views_bp.route('/add-note', methods=['POST'])
@login_required
def add_note():
    note_content = request.form.get('note')
    if note_content and note_content.strip(): # Sjekk at det ikke bare er mellomrom
        try:
            new_note_obj = Note(data=note_content, user_id=current_user.id)
            db.session.add(new_note_obj)
            db.session.commit()
            flash('Notat lagret!', category='success')
        except Exception as e:
             db.session.rollback()
             flash(f'Kunne ikke lagre notat: {e}', category='error')
             print(f"Error saving note: {e}")
    else:
        flash('Notatfeltet kan ikke være tomt.', category='error')
    return redirect(url_for('views_bp.notes'))

@views_bp.route('/delete-note/<int:note_id>', methods=['POST'])
@login_required
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id == current_user.id:
        try:
            db.session.delete(note)
            db.session.commit()
            flash('Notat slettet!', category='success')
        except Exception as e:
            db.session.rollback()
            flash(f'Kunne ikke slette notat: {e}', category='error')
            print(f"Error deleting note: {e}")
    else:
        flash('Ingen tilgang til å slette dette notatet.', category='error')
    return redirect(url_for('views_bp.notes'))


# ---------- REVIDERT KOMMENTAR-LAGRINGSRUTE ----------
# Ruten for å motta nye kommentarer
@views_bp.route('/add_comment/<page_name>', methods=['POST']) # Bruker page_name som en variabel del av URLen
@login_required # Krever at brukeren er logget inn
def add_comment(page_name):
    # Henter innholdet fra form-data
    content = request.form.get('content')

    # Validering: Sjekk at innholdet ikke er tomt
    if not content or not content.strip():
        flash("Kommentaren kan ikke være tom.", "error")
        # Omdirigerer tilbake til siden kommentaren kom fra
        # Vi må vite hvilken side vi skal tilbake til.
        # Det enkleste er å omdirigere basert på page_name,
        # men vi trenger en mapping fra page_name til url_for endpoint.
        # For nå, la oss hardkode for mattespill:
        if page_name == 'mattespill':
             return redirect(url_for('views_bp.spill_mattespill'))
        else:
             # Håndter andre sider her, eller en generell fallback
             return redirect(url_for('views_bp.home')) # Fallback til forsiden

    # Bruker den importerte insert_comment funksjonen fra queries.py
    # Sender med current_user.id (fra Flask-Login), side-identifikator og innhold
    success = insert_comment(user_id=current_user.id, page=page_name, content=content)

    # Gi tilbakemelding basert på om lagringen var vellykket
    if success:
        flash("Kommentar lagt til!", "success")
    else:
        flash("Kunne ikke lagre kommentaren. Prøv igjen.", "error")

    # Omdiriger tilbake til den relevante spillsiden (eller annen side)
    if page_name == 'mattespill':
        return redirect(url_for('views_bp.spill_mattespill'))
    # Legg til elif for andre sider som får kommentarer
    # elif page_name == 'snake':
    #    return redirect(url_for('views_bp.snake'))
    else:
        # Generell fallback hvis siden ikke er kjent
        return redirect(url_for('views_bp.home'))

# ---------- SLUTT PÅ REVIDERING AV KOMMENTAR-LAGRINGSRUTE ----------

# ---------- RUTE FOR TILBAKEMELDING ----------
@views_bp.route('/feedback', methods=['GET', 'POST'])
@login_required # Kun innloggede brukere kan gi feedback
def feedback():
    if request.method == 'POST':
        # Hent meldingen fra skjemaet
        message = request.form.get('message')

        # Enkel validering: Sjekk at meldingen ikke er tom eller bare mellomrom
        if not message or not message.strip():
            flash('Tilbakemeldingen kan ikke være tom.', category='error')
            # Ikke redirect her, la brukeren se skjemaet igjen med feilmeldingen
        else:
            # Prøv å lagre tilbakemeldingen ved hjelp av funksjonen fra queries.py
            success = add_feedback(user_id=current_user.id, message=message)

            if success:
                flash('Takk for din tilbakemelding!', category='success')
                # Omdiriger til en passende side, f.eks. hjemmesiden eller tilbake til feedback-siden
                return redirect(url_for('views_bp.feedback')) # Viser feedback-siden på nytt (med suksessmelding)
                # Alternativt: return redirect(url_for('views_bp.home'))
            else:
                flash('En feil oppstod. Kunne ikke lagre tilbakemeldingen. Prøv igjen.', category='error')
                # Ikke redirect her heller, la dem prøve igjen

    # Hvis det er en GET-request (eller POST feilet validering/lagring uten redirect)
    # Vis feedback-skjemaet
    return render_template("Feedback.html", user=current_user)

# ---------- RUTE FOR ADMIN TIL Å SE FEEDBACK ----------
@views_bp.route('/admin/feedback') # En URL som indikerer admin-område
@login_required # Krever innlogging
def view_feedback():
    # Sjekk om brukeren er admin
    if current_user.user_role != 'admin':
        # Hvis ikke admin, vis feilmelding og send dem bort
        flash('Du har ikke tilgang til denne siden.', category='error')
        return redirect(url_for('views_bp.home')) # Send til forsiden

    # Hvis brukeren ER admin:
    try:
        # Hent alle tilbakemeldinger fra databasen via queries.py
        all_feedbacks = get_all_feedback()
        # Vis Admin-Feedback.html-malen og send med listen over feedbacks
        return render_template("Admin-Feedback.html", user=current_user, feedbacks=all_feedbacks)
    except Exception as e:
        # Generell feilhåndtering hvis noe går galt med databasehenting
        flash('Kunne ikke hente tilbakemeldinger fra databasen.', category='error')
        print(f"Error fetching feedback for admin: {e}") # Logg feilen
        return redirect(url_for('views_bp.home')) # Send til forsiden ved feil

# ---------- SLUTT PÅ ADMIN FEEDBACK-RUTE ----------