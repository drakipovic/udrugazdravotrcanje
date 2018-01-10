from datetime import date, datetime

from flask import render_template, request, redirect, jsonify, url_for, session, g

from main import app
from models import User, League, Race, RaceResult


@app.before_request
def _before_request():
    if session.get('logged_in'):
        username = session['logged_in']
        g.user = User.query.filter_by(username=username).first()
        g.not_approved = len(User.query.filter_by(approved=False).all())

        return

    if 'not-approved' in request.url:
        return
    
    if 'static' in request.url:
        return

    if 'register' in request.url:
        return

    if 'login' in request.url and request.method == 'GET':
        return

    if 'logged_in' not in session and 'login' not in request.url:
        return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.json.get('username')
        password = request.json.get('password')
        remember_me = request.json.get('remember_me')
        
        user = User.query.filter_by(username=username).first()
        if user is None:
            return jsonify({'username': 'User not found!'}), 401

        if not user.check_password(password):
            return jsonify({'password': 'Wrong password!'}), 401

        if not user.approved:
            return jsonify({'not_approved': True})

        session['logged_in'] = username
        if remember_me:
            session.permanent = True

        return jsonify({'success': True, 'user': dict(user)})

    return render_template('login.html')


@app.route('/not-approved')
def not_approved():
    return render_template('not_approved.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.json.get('username')
        password = request.json.get('password')
        email = request.json.get('email')
        name = request.json.get('name')
        surname = request.json.get('surname')
        gender = request.json.get('gender')
        birthdate = request.json.get('birthdate')

        errors = []

        user = User.query.filter_by(username=username).first()
        if user:
            errors.append({"username": "Username already taken, please choose another."})
        
        if not username: errors.append({"username": "This field is required!"})
        if not password: errors.append({"password": "This field is required!"})
        if not email: errors.append({"email": "This field is required!"})
        if not name: errors.append({"name": "This field is required!"})
        if not surname: errors.append({"surname": "This field is required!"})
        if not gender: errors.append({"gender": "This field is required!"})
        if not birthdate: errors.append({"birthdate": "This field is required!"})

        if errors:
            return jsonify({"errors": errors}), 400
        
        birthdate = datetime.strptime(birthdate, "%d/%m/%Y")

        user = User(username, password, email, name, surname, gender, birthdate)
        user.save()

        return jsonify({"success": True, "user": dict(user)})

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.permanent = False

    return redirect(url_for('login'))


@app.route('/')
@app.route('/admin/dashboard')
def admin_dashboard():
    return render_template('admin/dashboard.html')


@app.route('/admin/users')
def admin_users():
    return render_template('admin/users.html')


@app.route('/admin/leagues')
def admin_leagues():
    leagues = [dict(league) for league in League.query.all()]
    return render_template('admin/leagues.html', leagues=leagues)


@app.route('/admin/leagues/<int:league_id>')
def admin_league(league_id):
    league = League.query.get(league_id)
    return render_template('admin/league.html', league=league)


@app.route('/admin/races/<race_id>')
def admin_race(race_id):
    race = Race.query.get(race_id)
    league = League.query.get(race.league_id)

    return render_template('admin/race.html', race=race, league=league)


@app.route('/profile')
@app.route('/profile/{username}')
def profile(username=None):
    if not username:
        user = g.user
    else:
        user = User.query.filter_by(username=username).first()

    return render_template('profile.html')


@app.route('/races')
def races():
    future_races = Race.query.filter(Race.start_time != None, Race.finished == False).limit(10)
    past_races = Race.query.filter(Race.finished == True).limit(10)
    
    future_leagues = [League.query.get(race.league_id) for race in future_races]
    past_leagues = [League.query.get(race.league_id) for race in past_races]

    my_results = [RaceResult.query.filter(RaceResult.race_id == race.race_id, 
                                        RaceResult.user_id == g.user.user_id).first()
                                        for race in future_races]

    return render_template('races.html', future_races=future_races, future_leagues=future_leagues, past_races=past_races, past_leagues=past_leagues, my_results=my_results)


@app.route('/races/<race_id>')
def race(race_id):
    race = Race.query.get(race_id)
    league = League.query.get(race.league_id)
    my_result = RaceResult.query.filter(RaceResult.race_id == race.race_id, 
                                        RaceResult.user_id == g.user.user_id).first()
    
    race_results = [dict(race_result) for race_result in race.race_results]
    return render_template('race.html', race=race, league=league, 
                                my_result=my_result, race_results=race_results)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404