from flask import render_template, request, redirect, jsonify, url_for, session, g

from main import app
from models import User, League, Race


# @app.before_request
# def _before_request():
#     if session.get('logged_in'):
#         username = session['logged_in']
#         g.user = User.query.filter_by(username=username).first()
#         return
    
#     if 'static' in request.url:
#         return

#     if request.url.endswith('admin'):
#         return

#     return redirect(url_for('login_admin'))


@app.before_request
def _before_request():
    g.user = User(username='dino', password='admin', name='Dino', surname='Rakipovic', gender='M', age=23)


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

        return jsonify({'success': True})

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.permanent = False

    return redirect(url_for('login_admin'))


@app.route('/')
@app.route('/admin/dashboard')
def admin_dashboard():
    return render_template('dashboard.html', user=g.user)


@app.route('/admin/leagues')
def admin_leagues():
    leagues = [dict(league) for league in League.query.all()]
    return render_template('leagues.html', user=g.user, leagues=leagues)


@app.route('/admin/leagues/<int:league_id>')
def admin_league(league_id):
    league = League.query.get(league_id)
    return render_template('league.html', user=g.user, league=league)


@app.route('/admin/races/<race_id>')
def admin_race(race_id):
    race = Race.query.get(race_id)
    league = League.query.get(race.league_id)

    return render_template('race.html', user=g.user, race=race, league=league)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404