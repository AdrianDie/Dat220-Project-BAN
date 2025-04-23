from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db  
from flask_login import login_user, login_required, logout_user, current_user

# Definerer en Blueprint med navnet 'auth_bp'
auth_bp = Blueprint('auth_bp', __name__)

# Rute for brukerinnlogging
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        user_password = request.form.get('user_password')

        # Henter brukeren fra databasen
        user = User.query.filter_by(username=user_name).first()
        if user:
            if check_password_hash(user.password, user_password):
                flash('Du er nå logget inn!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views_bp.home'))
            
            else:
                flash('Feil passord, prøv igjen.', category='error')

        else:
            flash('Brukernavn eksisterer ikke.', category='error')

    # Viser innloggingsiden
    return render_template("Login.html", user=current_user)

# Rute for brukerutlogging
@auth_bp.route('/logout')
@login_required
def logout():
    # Logger ut brukeren og omdirigerer til innloggingsiden
    logout_user()
    return redirect(url_for('auth_bp.login'))
    

# Rute for brukerregistrering
@auth_bp.route('/signup', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = ""

        # Bestemmer rollen til brukeren basert på antall eksisterende brukere
        user_count = User.query.count()
        if user_count == 0:
            role = "admin"
        else:
            role = "regular"
        
        user = User.query.filter_by(username=user_name).first()

        if user:
            flash('Brukernavn er allerede tatt', category='error')

        elif not user_name or user_name.strip() == "":
            flash("Brukernavn kan ikke være tomt.")

        elif len(user_name.replace(" ", "")) > 20:
            flash('Brukernavn må være kortere enn 20 tegn uten mellomrom', category='error')

        elif password.strip() == "":
            flash("Passord kan ikke være tomt.")

        elif len(password.replace(" ", "")) < 4:
            flash('Passordet må være minst 4 tegn uten mellomrom', category='error')

        elif password != confirm_password:
            flash('Passordene samsvarer ikke', category='error')
        else:
            # Oppretter en ny bruker, krypterer passordet og lagrer i databasen
            new_user = User(username=user_name, password=generate_password_hash(password, method='pbkdf2:sha256'), user_role=role)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Kontoen er opprettet!', category='success')
            return redirect(url_for('views_bp.home'))

    # Viser registreringssiden
    return render_template("Signup.html", user=current_user)

# Rute for å oppdatere brukerens passord
@auth_bp.route('/update-password', methods=['POST'])
@login_required
def update_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if new_password.strip() == "":
            flash("Passord kan ikke være tomt.")

        elif len(new_password.replace(" ", "")) < 4:
            flash('Passordet må være minst 4 tegn uten mellomrom', category='error')

        elif new_password != confirm_password:
            flash('Passordene samsvarer ikke.', category='error')

        elif current_password == new_password:
            flash('Nytt passord kan ikke være det samme som det gamle passordet', category='error')
        else:
            # Oppdaterer brukerens passord, krypterer det nye passordet og lagrer i databasen
            current_user.password = generate_password_hash(confirm_password, method='pbkdf2:sha256')
            db.session.commit()
            flash('Passordet er endret', category='success')
            return redirect(url_for('views_bp.settings'))
    
    # Viser siden for å endre passordet
    return render_template("settings.html", user=current_user)
