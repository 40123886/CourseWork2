import ConfigParser
import logging
import sqlite3

from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, url_for, g

app = Flask(__name__)
MovieDB = 'var/MovieDB.db'

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
    return render_template('index.html')
  except Exception, e:
    app.logger.error(e)

@app.route('/movies')
def movie():
  this_route = url_for('movie')
  app.logger.info("Select Movies Page" + this_route)
  try:
    db = get_db()
    cursor = db.execute('SELECT rowid, title FROM movie')
    movies = [dict(id=row[0], title=row[1]) for row in cursor.fetchall()]
    return render_template('movie.html', movies = movies)
  except Exception, e:
    app.logger.error(e)

@app.errorhandler(404)
def page_not_found(e):
  app.logger.error(e)
  return render_template('404.html'), 404

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
