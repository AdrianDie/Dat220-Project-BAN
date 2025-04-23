from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, send_from_directory, session # La til session for flash meldinger etc.
from flask_login import login_required, current_user
# Importerer funksjonene direkte fra queries
from .queries import * # Endret fra website.queries til .queries for relativ import
from .models import User, Files # Lagt til Comments her også
from . import db
import os
from .auth import update_password
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

# --- Score håndtering ---
@views_bp.route('/submit-score', methods=['POST'])
@login_required
def submit_score():
    data = request.get_json()
    score = data.get('score')
    user_id = current_user.id

    if score:
        new_score(user_id, score)
        return jsonify({"message": "Poengum lagret"}), 200
    return jsonify({"error": "Ingen poengsum oppgitt"}), 400

@views_bp.route('/high-scores')
@login_required
def high_scores():
    top_scores = get_best_scores(3)
    scores_data = [{"username": score, "score": name} for (score, name) in top_scores]
    return jsonify(scores_data)

# --- Brukeradmin ---
@views_bp.route('/oversikt-brukere')
@login_required
def brukeroversikt():
    if current_user.user_role == 'admin':
        search_query = request.args.get('search', '')
        users = get_users(f'%{search_query}%')
        return render_template('Oversikt-brukere.html', user=current_user, users=users)
    else:
        flash('Du har ikke tilgang til denne siden.', category='error')
        return redirect(url_for('views_bp.home'))

@views_bp.route('/delete-user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.user_role == 'admin':
        user_role = get_role(user_id)
        
        if user_role == 'regular':
            remove_user(user_id)
            flash('Bruker slettet', category='success')    
        elif user_role == 'admin':
            flash('Kan ikke slette brukere som ikke er "regular"', category='error')
        else:
            flash('Finner ikke bruker', category='eror')
    else:
        flash('Ingen tilgang', category='error')
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

# --- Notater ---
@views_bp.route('/notes', methods=['GET'])
@login_required
def notes():
    user_notes = get_notes(current_user.id)
    return render_template("Notes.html", user=current_user, notes=user_notes)

@views_bp.route('/add-note', methods=['POST'])
@login_required
def add_note():
    note_content = request.form.get('note')
    if note_content:
        new_note(note_content, current_user.id)
        flash('Notat lagret!', category='success')
    else:
        flash('Notatfeltet kan ikke være tom.', category='error')
    return redirect(url_for('views_bp.notes'))

@views_bp.route('/delete-note/<int:note_id>', methods=['POST'])
@login_required
def delete_note(note_id):
    if remove_note(note_id, current_user.id):
        flash('Notat slettet!', category='success')
    else:
        flash('Kunne ikke slette notat.', category='error')

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

@views_bp.route('/chat', methods=['GET'])
@login_required
def chat():
    previous_messages = get_chat(20)
    return render_template("Chat.html", user=current_user, messages=previous_messages)

@views_bp.route('/settings', methods=['GET'])
@login_required
def settings():
    # Get the user's biography
    biography = get_biography(current_user.id)
    return render_template("Settings.html", user=current_user, biography=biography)

@views_bp.route('/save-biography', methods=['POST'])
@login_required
def save_biography():
    biography = request.form.get('biography', '')
    
    set_biography(current_user.id, biography)
    flash('Biografi lagret!', category='success')
    
    return redirect(url_for('views_bp.settings'))

@views_bp.route('/profile/<username>', methods=['GET'])
@login_required
def profile(username):
    # Hent brukerdata
    user_info = collect_public_information(username)
    
    if not user_info:
        flash('Brukeren finnes ikke.', category='error')
        return redirect(url_for('views_bp.home'))
    
    profile_user = {
        'id': user_info['id'],
        'username': user_info['username']
    }
    
    return render_template("profile.html", 
                          user=current_user,
                          profile_user=profile_user,
                          biography=user_info['biography'],
                          bio_updated=user_info['bio_updated'])