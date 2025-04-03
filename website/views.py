from flask import Flask, Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .models import User, HighScores, Note
import json
from .queries import *
from . import db
import json

# Oppretter en Blueprint kalt 'views_bp' som brukes til å definere ruter og visninger for applikasjonen.
views_bp = Blueprint('views_bp', __name__)

# Sett opp en mappe for å lagre opplastede bilder (flyttes til app.py)
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Sjekk om en fil har en gyldig utvidelse
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Rute for å vise opplastingsskjema og håndtere opplasting
@views_bp.route('/files', methods=['GET', 'POST'])
@login_required
def files():
    if request.method == 'POST':
        return upload_file()
    
    user_files = Files.query.filter_by(user_id=current_user.id).all()  # Hent filer fra databasen
    return render_template("Files.html", user=current_user, files=user_files)

# Håndterer filopplasting
def upload_file():
    if 'file' not in request.files:
        flash('Ingen fil valgt', 'error')
        return redirect(url_for('views_bp.files'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('Ingen fil valgt', 'error')
        return redirect(url_for('views_bp.files'))
    
    if file and allowed_file(file.filename):
        filename = file.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Lagre filen i den eksterne "uploads"-mappen
        file.save(filepath)

        # Lagre filinfo i databasen
        new_file = Files(user_id=current_user.id, filename=filename)  
        db.session.add(new_file)
        db.session.commit()

        flash(f'Fil {filename} lastet opp og lagret i databasen!', 'success')
        return redirect(url_for('views_bp.files'))

    flash('Filtypen er ikke tillatt', 'error')
    return redirect(url_for('views_bp.files'))



@views_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)



# Forsidevisning
@views_bp.route('/')
def home():
    return render_template("Forside.html", user=current_user)

# Spillvisning
@views_bp.route('/mattespill')
@login_required
def spill():
    return render_template("Spill-mattespill.html", user=current_user)

# Snake-spillvisning
@views_bp.route('/snake')
@login_required
def snake():
    return render_template("Spill-snake.html", user=current_user)

# Sender score til serveren for lagring i databasen
@views_bp.route('/submit-score', methods=['POST'])
@login_required
def submit_score():
    data = request.get_json()
    
    score = data.get('score')
    user_id = current_user.id

    if score:
        new_score(user_id, score)
        return jsonify({"message": "Poengsum lagret"}), 200
    return jsonify({"error": "Ingen poengsum oppgitt"}), 400

# Henter de tre høyeste poengsummene fra databasen og returnerer dem som JSON
@views_bp.route('/high-scores')
@login_required
def high_scores():
    top_scores = get_best_scores(3)
    scores_data = [{"username": score, "score": name} for (score, name) in top_scores]
    return jsonify(scores_data)

# Brukeroversikt for administratorer
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

# Sletter bruker fra databasen (kun for administratorer)
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

# Sprettballen-spillvisning (krever pålogging)
@views_bp.route('/sprettball')
@login_required
def sprettballen():
    return render_template("Spill-sprettball.html", user=current_user)

# Bildegate-visning (krever pålogging)
@views_bp.route('/bildegate')
@login_required
def bilde_gate():
    return render_template("Spill-bildegater.html", user=current_user)

# Spillside-visning (krever pålogging)
@views_bp.route('/oversikt-spill')
@login_required
def spillside():
    return render_template("Oversikt-spill.html", user=current_user)

# Notatsidevisning (krever pålogging)
@views_bp.route('/notes', methods=['GET'])
@login_required
def notes():
    user_notes = get_notes(current_user.id)
    return render_template("Notes.html", user=current_user, notes=user_notes)

# Legger til et nytt notat til databasen
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

# Sletter et notat fra databasen
@views_bp.route('/delete-note/<int:note_id>', methods=['POST'])
@login_required
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id == current_user.id:  # Sikrer at kun eieren kan slette notatet
        db.session.delete(note)
        db.session.commit()
        flash('Notat slettet!', category='success')
    else:
        flash('Ingen tilgang til å slette dette notatet.', category='error')
    return redirect(url_for('views_bp.notes'))