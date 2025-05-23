from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, send_from_directory, g, session
from .queries import *
import os
from .auth import login_required
# Oppretter en Blueprint kalt 'views_bp'
views_bp = Blueprint('views_bp', __name__)

# Setter opp mappe for opplastede filer (bør ideelt sett konfigureres i app/__init__.py)
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads') # Pass på at 'uploads' mappen finnes i roten av prosjektet
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Sjekk om en fil har en gyldig utvidelse
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@views_bp.route('/files', methods=['GET', 'POST'])
@login_required
def files():
    if request.method == 'POST':
        return upload_file()

    # Use get_files function instead of Files.query
    user_files = get_files(g.user.id)
    return render_template("Files.html", user=g.user, files=user_files)

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
            # Use insert_file function instead of SQLAlchemy
            insert_file(g.user.id, filename)
            flash(f'Fil {filename} lastet opp!', 'success')
        except Exception as e:
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

@views_bp.route('/')
def home():
    token = session.get('token')
    user_id = validate_session(token) if token else None
    user_data = get_user_by_id(user_id) if user_id else None
    
    # Create User class once
    class User:
        pass
    
    g.user = User()
    
    # Set default values for anonymous users
    g.user.id = '0' 
    g.user.username = 'Guest'
    g.user.user_role = 'guest'
    g.user.is_authenticated = False
    
    # Override with actual user data if available
    if user_data:
        g.user.id = user_id
        g.user.username = user_data['username']
        g.user.user_role = user_data['user_role']
        g.user.is_authenticated = True
    
    return render_template("Forside.html", user=g.user)

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
    return render_template("Spill-mattespill.html", user=g.user, comments=comments, page_name=page_identifier)

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
    return render_template("Spill-snake.html", user=g.user)

# --- Score håndtering ---
@views_bp.route('/submit-score', methods=['POST'])
@login_required
def submit_score():
    data = request.get_json()
    score = data.get('score')
    user_id = g.user.id

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
    if g.user.user_role == 'admin':
        search_query = request.args.get('search', '')
        users = get_users(f'%{search_query}%')
        return render_template('Oversikt-brukere.html', user=g.user, users=users)
    else:
        flash('Du har ikke tilgang til denne siden.', category='error')
        return redirect(url_for('views_bp.home'))

@views_bp.route('/delete-user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if g.user.user_role == 'admin':
        # Prevent admin from deleting themselves
        if int(user_id) == int(g.user.id):
            flash('Du kan ikke slette din egen konto her.', category='error')
            return redirect(url_for('views_bp.brukeroversikt'))
            
        user_role = get_role(user_id)
        # CRUD - Delete
        # Inne i delete_user funksjonen, etter sjekk om brukeren er admin og ikke sletter seg selv
        if user_role == 'regular':
            remove_user(user_id)
            # PÅ DENNE LINJEN: Kalles funksjonen remove_user. 
            # Brukeren med den gitte user_id fra databasen (DELETE).
            # Denne funksjonen lar en administrator (g.user.user_role == 'admin') slette en annen bruker som har rollen 'regular'. 
            # Funksjonskallet remove_user(user_id) er stedet der selve slettingen av bruker-entiteten utføres.
        elif user_role == 'admin':
            flash('Kan ikke slette brukere som ikke er "regular"', category='error')
        else:
            flash('Finner ikke bruker', category='error')  # Fixed typo in category
    else:
        flash('Ingen tilgang', category='error')
    return redirect(url_for('views_bp.brukeroversikt'))
# --- Andre spill (uendret) ---
@views_bp.route('/sprettball')
@login_required
def sprettballen():
    return render_template("Spill-sprettball.html", user=g.user)

@views_bp.route('/bildegate')
@login_required
def bilde_gate():
    return render_template("Spill-bildegater.html", user=g.user)

@views_bp.route('/oversikt-spill')
@login_required
def spillside():
    return render_template("Oversikt-spill.html", user=g.user)

# --- Notater ---
@views_bp.route('/notes', methods=['GET'])
@login_required
def notes():
    #CRUD- Read
    user_notes = get_notes(g.user.id)

    return render_template("Notes.html", user=g.user, notes=user_notes)

@views_bp.route('/add-note', methods=['POST'])
@login_required
def add_note():
    note_content = request.form.get('note')
    #CRUD - create
    if note_content:
        new_note(note_content, g.user.id)
        flash('Notat lagret!', category='success')
    else:
        flash('Notatfeltet kan ikke være tom.', category='error')
    return redirect(url_for('views_bp.notes'))

@views_bp.route('/update-note/<int:note_id>', methods=['POST'])
@login_required
def update_note(note_id):
    note_content = request.form.get('note')

    # CRUD- Update
    if note_content:
        update_note_content(note_id, g.user.id, note_content)
        flash('Notat Oppdatert!', category='success')
    else:
        flash('Notatfeltet kan ikke være tom.', category='error')
    return redirect(url_for('views_bp.notes'))

@views_bp.route('/delete-note/<int:note_id>', methods=['POST'])
@login_required
def delete_note(note_id):
    #CRUD - Delete
    if remove_note(note_id, g.user.id):
        flash('Notat slettet!', category='success')
    else:
        flash('Kunne ikke slette notat.', category='error')

    return redirect(url_for('views_bp.notes'))

@views_bp.route('/add_comment/<page_name>', methods=['POST']) 
@login_required 
def add_comment(page_name):
    content = request.form.get('content')

    if not content or not content.strip():
        flash("Kommentaren kan ikke være tom.", "error")
        if page_name == 'mattespill':
             return redirect(url_for('views_bp.spill_mattespill'))
        else:
             return redirect(url_for('views_bp.home'))
        
    success = insert_comment(user_id=g.user.id, page=page_name, content=content)

    if success:
        flash("Kommentar lagt til!", "success")
    else:
        flash("Kunne ikke lagre kommentaren. Prøv igjen.", "error")

    if page_name == 'mattespill':
        return redirect(url_for('views_bp.spill_mattespill'))
    else:
        return redirect(url_for('views_bp.home'))

@views_bp.route('/chat', methods=['GET'])
@login_required
def chat():
    previous_messages = get_chat(20)
    return render_template("Chat.html", user=g.user, messages=previous_messages)

@views_bp.route('/settings', methods=['GET'])
@login_required
def settings():
    biography = get_biography(g.user.id)
    session_count = get_session_count(g.user.id)
    return render_template("Settings.html", user=g.user, biography=biography, session_count=session_count)

@views_bp.route('/clear-sessions', methods=['POST'])
@login_required
def clear_sessions():
    current_token = session.get('token')
    deleted_count = clear_sessions_except_current(g.user.id, current_token)
    
    if deleted_count > 0:
        flash(f'Alle andre økter er nå logget ut.', category='success')
    else:
        flash('Ingen andre aktive økter ble funnet.', category='info')
    
    return redirect(url_for('views_bp.settings'))
@views_bp.route('/save-biography', methods=['POST'])
@login_required
def save_biography():
    biography = request.form.get('biography', '')
    
    set_biography(g.user.id, biography)
    flash('Biografi lagret!', category='success')
    
    return redirect(url_for('views_bp.settings'))

@views_bp.route('/profile/<username>', methods=['GET'])
@login_required
def profile(username):
    user_info = collect_public_information(username)
    
    if not user_info:
        flash('Brukeren finnes ikke.', category='error')
        return redirect(url_for('views_bp.home'))
    
    profile_user = {
        'id': user_info['id'],
        'username': user_info['username']
    }
    
    return render_template("profile.html", 
                          user=g.user,
                          profile_user=profile_user,
                          biography=user_info['biography'],
                          bio_updated=user_info['bio_updated'],
                          time_created=user_info['time_created'])


@views_bp.route('/feedback', methods=['GET', 'POST'])
@login_required 
def feedback():
    if request.method == 'POST':
        message = request.form.get('message')

        if not message or not message.strip():
            flash('Tilbakemeldingen kan ikke være tom.', category='error')
        else:
            success = add_feedback(user_id=g.user.id, message=message)

            if success:
                flash('Takk for din tilbakemelding!', category='success')
                return redirect(url_for('views_bp.feedback')) 
            else:
                flash('En feil oppstod. Kunne ikke lagre tilbakemeldingen. Prøv igjen.', category='error')
              

   
    return render_template("Feedback.html", user=g.user)

# ---------- RUTE FOR ADMIN TIL Å SE FEEDBACK ----------
@views_bp.route('/admin/feedback') 
@login_required
def view_feedback():
    
    if g.user.user_role != 'admin':
       
        flash('Du har ikke tilgang til denne siden.', category='error')
        return redirect(url_for('views_bp.home')) 

    # Hvis brukeren ER admin:
    try:

        all_feedbacks = get_all_feedback()
        return render_template("Admin-Feedback.html", user=g.user, feedbacks=all_feedbacks)
    except Exception as e:
        flash('Kunne ikke hente tilbakemeldinger fra databasen.', category='error')
        print(f"Error fetching feedback for admin: {e}") 
        return redirect(url_for('views_bp.home')) 

# ---------- SLUTT PÅ ADMIN FEEDBACK-RUTE ----------
