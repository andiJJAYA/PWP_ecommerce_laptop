from flask import Blueprint, render_template, request, redirect, flash, jsonify 
from flask_login import login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from extensions import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    submitted = False

    if request.method == 'POST':
        submitted = True

        if request.is_json:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
        else:
            email = request.form['email']
            password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if not user:
            if request.is_json:
                return jsonify({"status": "error", "message": "Akun belum terdaftar"}), 401
            flash('Akun belum terdaftar')
            return render_template('auth/login.html', submitted=submitted)

        if not check_password_hash(user.password_hash, password):
            if request.is_json:
                return jsonify({"status": "error", "message": "Password salah"}), 401
            flash('Password salah')
            return render_template('auth/login.html', submitted=submitted)

        login_user(user)

        if request.is_json:
            return jsonify({
                "status": "success", 
                "message": "Login successful",
                "user": {"email": user.email, "role": user.role}
            }), 200

        if user.role == 'admin':
            return redirect('/admin')
        return redirect('/')

    return render_template('auth/login.html', submitted=submitted)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User(
            nama=request.form['nama'],
            email=request.form['email'],
            password_hash=generate_password_hash(request.form['password'])
        )
        db.session.add(user)
        db.session.commit()
        return redirect('/login')

    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect('/')
