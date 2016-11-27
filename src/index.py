import ConfigParser
import logging
import sqlite3

from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, url_for, g, request, redirect, Response, flash, abort
from forms import add
from werkzeug import secure_filename
from flask_login import LoginManager, UserMixin, login_required

app = Flask(__name__)
app.secret_key = 'this_is_the_secret_key'
MovieDB = 'var/MovieDB.db'
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
  user_databse = {"JohnDoe": ("JohnDoe", "John"),
                  "JaneDoe": ("JaneDoe", "Jane")}

def __init__(self, username, password):
  self.id = username
  self.password = password

@login_manager.request_loader
def load_user(request):
  token = request.headers.get('Authorisation')
  if token is None:
    token = request.args.get('token')

  if token is not None:
    username, password = token.split(":")
    user_entry = User.get(username)
    if (user_entry is not None):
      user = User(user_entry[0], user_entry[1])
      if (user.password == password):
        return user
  return None

@classmethod
def get(cls, id):
  return cls.user_database.get(id)

def get_db():
  db = getattr(g, 'db', None)
  if  db is None:
        db = sqlite3.connect(MovieDB)
        g.db = db
  return db

@app.teardown_appcontext
def close_db_connection(exception):
    db = getattr(g, 'db', None)
    if db is not None:
      db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.route('/')
def root():
  this_route = url_for('.root')
  app.logger.info("Index - " + this_route)
  try:
    db = get_db()
    cursor = db.execute(''' SELECT poster, title, tagline, overview, id FROM movie
    ORDER BY id DESC LIMIT 1''')
    movie = [dict(poster=row[0], title=row[1], tagline=row[2], overview=row[3],
      id=row[4])
    for row in cursor.fetchall()]
    return render_template('index.html', movies = movie)
  except Exception, e:
    app.logger.error(e)

@app.route('/movies')
def movies():
  this_route = url_for('movies')
  app.logger.info("Select Movies Page" + this_route)
  try:
    db = get_db()
    cursor = db.execute('''SELECT rowid, title, poster FROM movie ''')
    movies = [dict(id=row[0], title=row[1], poster=row[2]) for row in cursor.fetchall()]
    return render_template('movie.html', movies = movies)
  except Exception, e:
    app.logger.error(e)

@app.route('/actors')
def actors():
  this_route = url_for('actors')
  app.logger.info("Select Actor Page" + this_route)
  try:
    db = get_db()
    cursor = db.execute('''SELECT rowid, first_name, last_name, birth_name, picture FROM actor ''')
    actors = [dict(id=row[0], first_name=row[1], last_name=row[2],
    birth_name=row[3], picture=row[4]) for row in cursor.fetchall()]
    return render_template('actor.html', actors = actors)
  except Exception, e:
    app.logger.error(e)

@app.route('/movies/selected', methods=['POST', 'GET'])
def selected_movie():
  this_route = url_for('selected_movie')
  app.logger.info("Selected a movie" + this_route)
  try:
    movieid = request.args.get('movieid', '')
    db = get_db()
    cursor_movie = db.execute('''SELECT title, tagline, overview, runtime,
      release_date, revenue, poster FROM movie m WHERE m.id = ? ''', [movieid])
    movie = [dict(title=row[0], tagline=row[1], overview=row[2],
      runtime=row[3], release=row[4], revenue=row[5], poster=row[6]) for row in
      cursor_movie.fetchall()]
    cursor_genre = db.execute('''SELECT genre FROM genre g INNER JOIN
      movie_genre_key gk ON g.id=gk.genre_id WHERE gk.movie_id = ? AND g.id <>
      19''', [movieid])
    genres = [dict(genre=row[0]) for row in cursor_genre.fetchall()]
    cursor_cast = db.execute('''SELECT a.id, first_name, last_name, birth_name FROM
      actor a INNER JOIN movie_actor_key ak ON a.id=ak.actor_id WHERE
      ak.movie_id = ? ''', [movieid])
    actors = [dict(id=row[0], fname=row[1], lname=row[2], bname=row[3]) for row in
      cursor_cast.fetchall()]
    return render_template('selected_movie.html', movie=movie, genre=genres, actor=actors, movieid=movieid)
  except Exception, e:
    app.logger.error(e)

@app.route('/actors/selected')
def selected_actor():
  this_route = url_for('selected_actor')
  app.logger.info("Selected Actor Page" + this_route)
  try:
    actorid = request.args.get('actorid', '')
    db = get_db()
    cursor_cast = db.execute('''SELECT first_name, last_name, birth_name, biography,
      date_of_birth, date_of_death, picture FROM actor WHERE id = ? ''', [actorid])
    actors = [dict(first_name=row[0], last_name=row[1], birth_name=row[2],
      biog=row[3], dob=row[4], dod=row[5], picture=row[6]) for row in
      cursor_cast.fetchall()]
    cursor_movies = db.execute('''SELECT m.id, title FROM movie m INNER JOIN
      movie_actor_key ak ON m.id=ak.movie_id WHERE ak.actor_id = ? ''', [actorid])
    movies = [dict(id=row[0], title=row[1]) for row in cursor_movies.fetchall()]
    return render_template('selected_actor.html', actors = actors,
      movies=movies, actorid=actorid)
  except Exception, e:
    app.logger.error(e)

@app.route('/loggedin')
@login_required
def loggedin():
  this_route = url_for('loggedin')
  app.logger.info("logged in page" + this_route)
  try:
    return "If you read this you are logged in"
  except Exception, e:
    app.logger.error(e)

@app.route('/add_movie', methods=['GET', 'POST'])
def add_movie():
  this_route = url_for('add_movie')
  app.logger.info("Adding a Film" + this_route)
  try:
    form = add()
    db = get_db()
    getmovieid = db.execute('''SELECT MAX(id)+1 FROM movie''')
    movieid = [dict(id=row[0]) for row in getmovieid.fetchall()]
    getgenres = db.execute('''SELECT id, genre FROM genre ORDER BY id DESC''')
    genres = [dict(id=row[0], genre=row[1]) for row in getgenres.fetchall()]
    if request.method == 'POST':
      id = request.form.get('movieid')
      title = request.form.get('title')
      tagline = request.form.get('tagline')
      overview = request.form.get('overview')
      runtime = request.form.get('runtime')
      release = request.form.get('release')
      revenue = request.form.get('revenue')
      poster = 'null'
      genre = request.form.get('genre')
      genre2 = request.form.get('genre2')
      genre3 = request.form.get('genre3')
      db.execute('''INSERT INTO movie VALUES (?, ?, ?, ?, ?, ?, ?, ?)
      ''', (id, title, tagline, overview, runtime, release,
      revenue, poster))
      db.execute('''INSERT INTO movie_genre_key VALUES (?, ?), (?, ?), (?,
      ?)''', (id, genre, id, genre2, id, genre3))
      db.commit()
      return redirect(url_for('add_actor'))
    else:
      return render_template('add_movie.html', form=form, movieid=movieid,
      genres=genres)
  except Exception, e:
    app.logger.error(e)

@app.route('/add_actor', methods=['GET', 'POST'])
def add_actor():
  this_route = url_for('add_actor')
  app.logger.info("Adding actor" + this_route)
  try:
    return redirect(url_for('/'))
  except Exception, e:
    app.logger.error(e)

@app.errorhandler(404)
def page_not_found(e):
  app.logger.error(e)
  return render_template('404.html'), 404

@app.errorhandler(401)
def unauthorised(e):
  app.logger.error(e)
  return render_template('401.html')

def init(app):
  config = ConfigParser.ConfigParser()
  try:
      config_location = "etc/defaults.cfg"
      config.read(config_location)

      app.config['DEBUG'] = config.get("config", "debug")
      app.config['ip_address'] = config.get("config", "ip_address")
      app.config['port'] = config.get("config", "port")
      app.config['url'] =  config.get("config", "url")

      app.config['log_file'] = config.get("logging", "name")
      app.config['log_location'] = config.get("logging", "location")
      app.config['log_level'] = config.get("logging", "level")
  except:
      print "Could not read the config file from", config_location

def logs(app):
    log_pathname = app.config['log_location'] + app.config['log_file']
    file_handler = RotatingFileHandler(log_pathname, maxBytes=1024*1024*10, backupCount=1024)
    file_handler.setLevel(app.config['log_level'])
    formatter = logging.Formatter("%(levelname)s | %(asctime)s | %(module)s | %(funcName)s | %(message)s" )
    file_handler.setFormatter(formatter)
    app.logger.setLevel( app.config['log_level'] )
    app.logger.addHandler(file_handler)

if __name__ == ("__main__"):
  init(app)
  logs(app)
  app.run(
      host=app.config['ip_address'],
      port=int(app.config['port']))
