from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import ARRAY

db = SQLAlchemy()


class Venue(db.Model):
    __tablename__ = "Venue"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(30))
    state = db.Column(db.String(30))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(30))
    image_link = db.Column(db.String(600))
    facebook_link = db.Column(db.String(600))
    genres = db.Column(ARRAY(db.String(200)))
    website = db.Column(db.String(600))
    seeking_talent = db.Column(db.String(4))
    seeking_description = db.Column(db.String(120))


class Artist(db.Model):

    __tablename__ = "Artist"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(30))
    state = db.Column(db.String(30))
    phone = db.Column(db.String(120))
    genres = db.Column(ARRAY(db.String(200)))
    image_link = db.Column(db.String(600))
    facebook_link = db.Column(db.String(600))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.String(4), default=False)
    seeking_description = db.Column(db.String(120))


class Show(db.Model):
    """ Model Show links Artists and Venues"""

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)
    venue_name = db.relationship("Venue", backref=db.backref("shows"))
    artist = db.relationship("Artist", backref=db.backref("shows"))
