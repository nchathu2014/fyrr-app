#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    seeking_description = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    shows = db.relationship('Show',cascade="all, delete", backref='Venue', lazy=True)

    def __repr__(self):
        return f'<Venue ID: {self.id}, name: {self.name}>'

    

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='Artist', lazy=True)

    def __repr__(self):
        return f'<Artist ID: {self.id}, name: {self.name}>'


class Show(db.Model):
  __tablename__ = 'Show'
  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime, nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)