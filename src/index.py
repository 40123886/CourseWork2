import ConfigParser
import logging

from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, url_for

app = Flask(__name__)

@app.route('/')
def root():
  this_route = url_for('.root')
  app.logger.info("Index - " + this_route)
  try:
    return render_template('index.html')
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
