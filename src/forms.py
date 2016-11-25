from flask_wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired

class add(Form):
  movieid = StringField('movieid', validators=[DataRequired])
  title = StringField('title', validators=[DataRequired])
  tagline = StringField('tagline', validators=[DataRequired])
  overview = StringField('overview', validators=[DataRequired])
  runtime = StringField('runtime', validators=[DataRequired])
  release = StringField('release', validators=[DataRequired])
  revenue = StringField('revenue', validators=[DataRequired])
