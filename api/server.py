from flask import Flask, render_template, request, redirect, make_response, url_for
from flask_sqlalchemy import SQLAlchemy

from Flask_music.api.parser import parse_songs

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rest_t.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


@app.route('/home')
def render_home():
    log = request.cookies.get('logged')
    if log == 'True':
        username = request.cookies.get('username')
        return render_template('home.html', username=username)
    else:
        return redirect('login')


@app.route('/users')
def render_users():
    users = User.query.all()
    return render_template('users.html', users=users)


@app.route('/')
def render():
    resp = make_response(render_template('home.html'))
    resp.set_cookie('logged', 'False')
    resp.headers['location'] = url_for('render_home')
    return resp, 302


@app.route('/update', methods=('POST', 'GET'))
def render_update():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username'])
        user.update({'username': request.form['new_username']})
        db.session.commit()
        return redirect('/users')
    else:
        return render_template('update.html')


@app.route('/charts', methods=('GET', 'POST'))
def charts():
    username = request.cookies.get('username')
    if username:
        songs = parse_songs()
        if request.method == 'GET':
            return render_template('songs.html', songs=songs)
        else:
            user = User.query.filter_by(username=username).first()
            song = MusicCompositions(
                user_id=user.id,
                song_name=request.form['song_name'],
                song_author=request.form['song_author']

            )
            db.session.add(song)
            db.session.commit()
            resp = make_response(render_template('songs.html', songs=songs))
            return resp
    else:
        return redirect('login')


@app.route('/mysongs')
def render_my_songs():
    username = request.cookies.get('username')
    if username:
        user_id = User.query.filter_by(username=username).first().id
        songs = MusicCompositions.query.filter_by(user_id=user_id)
        return render_template('mysongs.html', songs=songs)
    else:
        return redirect('login')


@app.route('/registration', methods=('GET', 'POST'))
def render_register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        user = User(
            username=username,
            password=password,
            email=email
        )
        try:
            db.session.add(user)
            db.session.commit()
            return redirect('/login')
        except:
            return redirect('/NIHUYA')

    else:
        return render_template('register.html')


@app.route('/login', methods=('POST', 'GET'))
def render_login():
    if request.cookies.get('logged') == 'False':
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            user = User.query.filter_by(username=username).first()
            if not user:
                return redirect('Wrong_password_or_login')
            if password != user.password or username != user.username:
                return redirect('Wrong_password_or_login')
            else:
                resp = make_response(render_template('home.html'))
                resp.set_cookie('logged', 'True')
                resp.set_cookie('username', username)
                resp.headers['location'] = url_for('render_home')
                return resp, 302
        else:
            return render_template('login.html')
    else:
        return redirect('home')


@app.route('/logout')
def logout():
    if request.cookies.get('logged') == 'False':
        return redirect('login')
    resp = make_response(render_template('login.html'))
    resp.set_cookie('logged', 'False')
    resp.headers['location'] = url_for('render_home')
    return resp, 302


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)


class MusicCompositions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    song_name = db.Column(db.String(50))
    song_author = db.Column(db.String(50))


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
    db.create_all()

