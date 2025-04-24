from flask import Blueprint, render_template, request, flash, redirect, url_for, session, g
from functools import wraps
from .queries import *

auth_bp = Blueprint('auth_bp', __name__)

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = session.get('token')
        user_id = validate_session(token)

        if not token or not user_id:
            flash('Du må logge inn for å se denne siden.', category='error')
            return redirect(url_for('auth_bp.login'))
        
        user_data = get_user_by_id(user_id)

        if not user_data:
            flash('Vennligst logg inn på nytt.', category='error')
            if token:
                delete_session(token)
            session.pop('token', None)
            return redirect(url_for('auth_bp.login'))  

        class User:
            pass
        g.user = User()

        g.user.id = user_id
        g.user.username = user_data['username']
        g.user.user_role = user_data['user_role']
        g.user.is_authenticated = True
        
        return f(*args, **kwargs)
    return wrapper

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        user_password = request.form.get('user_password')

        user_id = verify_password(user_name, user_password)
        
        if user_id:
            token = create_session(user_id)
            session['token'] = token

            g.user = get_user_by_id(user_id)
            
            flash('Du er nå logget inn!', category='success')
            response = redirect(url_for('views_bp.home'))
            response.set_cookie('auth_token', token)
            return response
        else:
            flash('Feil brukernavn eller passord.', category='error')

    return render_template("Login.html", user=None)

@auth_bp.route('/logout')
@login_required
def logout():
    token = session.get('token')
    if token:
        delete_session(token)
    
    session.pop('token', None)
    flash('Du er nå logget ut.', category='success')

    response = redirect(url_for('auth_bp.login'))
    response.delete_cookie('auth_token')
    return response

@auth_bp.route('/signup', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not user_name or user_name.strip() == "":
            flash("Brukernavn kan ikke være tomt.")
            return render_template("Signup.html", user=None)
            
        if len(user_name.replace(" ", "")) > 20:
            flash('Brukernavn må være kortere enn 20 tegn uten mellomrom', category='error')
            return render_template("Signup.html", user=None)
            
        if password.strip() == "":
            flash("Passord kan ikke være tomt.")
            return render_template("Signup.html", user=None)
            
        if len(password.replace(" ", "")) < 4:
            flash('Passordet må være minst 4 tegn uten mellomrom', category='error')
            return render_template("Signup.html", user=None)
            
        if password != confirm_password:
            flash('Passordene samsvarer ikke', category='error')
            return render_template("Signup.html", user=None)

        if check_username_exists(user_name):
            flash('Brukernavn er allerede tatt', category='error')
            return render_template("Signup.html", user=None)
        
        user_id = create_user(user_name, password)
        if user_id:
            token = create_session(user_id)
            session['token'] = token
            
            flash('Kontoen er opprettet!', category='success')
            response = redirect(url_for('views_bp.home'))
            response.set_cookie('auth_token', token)
            return response
        else:
            flash('Kunne ikke opprette konto. Prøv igjen.', category='error')

    return render_template("Signup.html", user=None)

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
            return redirect(url_for('views_bp.settings'))

        if len(new_password.replace(" ", "")) < 4:
            flash('Passordet må være minst 4 tegn uten mellomrom', category='error')
            return redirect(url_for('views_bp.settings'))

        if new_password != confirm_password:
            flash('Passordene samsvarer ikke.', category='error')
            return redirect(url_for('views_bp.settings'))

        if current_password == new_password:
            flash('Nytt passord kan ikke være det samme som det gamle passordet', category='error')
            return redirect(url_for('views_bp.settings'))
            
        if verify_password(g.user.username, current_password):
            if change_user_password(g.user.id, new_password):
                flash('Passordet er endret', category='success')
            else:
                flash('Kunne ikke endre passord. Prøv igjen.', category='error')
        else:
            flash('Nåværende passord er feil.', category='error')
            
        return redirect(url_for('views_bp.settings'))
    
    return redirect(url_for('views_bp.settings'))
