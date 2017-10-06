from flask import render_template, request, redirect, jsonify, url_for, session

from main import app
from models import User


@app.route('/admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        username = request.json.get('username')
        password = request.json.get('password')
        remember_me = request.json.get('remember_me')

        user = User.query.filter_by(username=username).first()
        if user is None:
            return jsonify({'username': 'User not found!'}), 401

        if not user.check_password(password):
            return jsonify({'password': 'Wrong password!'}), 401

        session['logged_in'] = username
        if remember_me:
            session.permanent = True

        print session
        print session['logged_in']

        return jsonify({'success': True})

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():

    return render_template('dashboard.html')