from flask import render_template, request, redirect, jsonify, url_for, session, g

from main import app
from models import User


@app.before_request
def _before_request():
    if session.get('logged_in'):
        username = session['logged_in']
        g.user = User.query.filter_by(username=username).first()
        return
    
    if 'static' in request.url:
        return

    if 'admin' in request.url and request.method == 'GET':
        return

    if 'logged_in' not in session and 'admin' not in request.url:
        return redirect(url_for('login_admin'))


@app.route('/admin', methods=['GET', 'POST'])
def login_admin():
    print request
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

        return jsonify({'success': True})

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.permanent = False

    return redirect(url_for('login_admin'))


@app.route('/')
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', name=g.user.name, surname=g.user.surname)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404