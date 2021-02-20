#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from forms import *
from models import app, db, Venue, Artist, Show


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  areas = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state)
  data = []
  for area in areas:
    venues = db.session.query(Venue).filter_by(state=area.state).filter_by(city=area.city).all()
    venue_data = []
    for venue in venues:
      venue_data.append({
        'id':venue.id,
        'name':venue.name,
        'num_upcoming_shows': len(db.session.query(Show).filter(Show.venue_id==venue.id).filter(Show.start_time>datetime.now()).all())
      })
    data.append({
      'city':area.city,
      'state':area.state,
      'venues':venue_data
      })
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '') 
  venues = db.session.query(Venue).filter(Venue.name.ilike('%'+search_term+'%')).all()
  data = []
  for venue in venues:
    data.append({
      "id" : venue.id,
      "name" : venue.name,
      "num_upcoming_shows": len(db.session.query(Show).filter(Show.venue_id==venue.id).filter(Show.start_time>datetime.now()).all())
    })
  response={
     "count": len(venues),
     "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue_data = db.session.query(Venue).filter_by(id=venue_id).all()
  data = []
  for venue in venue_data:
    venue_data = []
    u_shows = db.session.query(Show).filter(Show.venue_id==venue.id).filter(Show.start_time>datetime.now()).all()
    p_shows = db.session.query(Show).filter(Show.venue_id==venue.id).filter(Show.start_time<datetime.now()).all()

    upcoming_shows = []
    for show in u_shows:
      artist = db.session.query(Artist).filter(show.artist_id==Artist.id).all()[0]
      upcoming_shows.append({
        "artist_id": artist.id,
        "artist_image_link": artist.image_link,
        "artist_name": artist.name,
        "start_time": str(show.start_time)
      })

    past_shows = []
    for show in p_shows:
      artist = db.session.query(Artist).filter(show.artist_id==Artist.id).all()[0]
      past_shows.append({
        "artist_id": artist.id,
        "artist_image_link": artist.image_link,
        "artist_name": artist.name,
        "start_time": str(show.start_time)
      })

    data.append({
      "id" : venue.id,
      "name": venue.name,
      "genres": venue.genres,
      "address": venue.address,
      "city":venue.city,
      "state":venue.state,
      "phone": venue.phone,
      "website": venue.website,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link":venue.image_link,
      "upcoming_shows": upcoming_shows,
      "past_shows": past_shows,
      "past_shows_count": len(db.session.query(Show).filter(Show.venue_id==venue.id).filter(Show.start_time<datetime.now()).all()),
      "upcoming_shows_count": len(db.session.query(Show).filter(Show.venue_id==venue.id).filter(Show.start_time>datetime.now()).all())
  })

  return render_template('pages/show_venue.html', venue=data[0])

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)

  error = False
  try:
    venue = Venue(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      address = form.address.data,
      phone = form.phone.data,
      genres = form.genres.data,
      website = form.website.data,
      seeking_talent = form.seeking_talent.data,
      seeking_description = form.seeking_description.data,
      image_link = form.image_link.data,
      facebook_link = form.facebook_link.data
    )
    db.session.add(venue)
    db.session.commit()
    venue_id = venue.id
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    return render_template('pages/home.html')
  else:
    return redirect(url_for('show_venue', venue_id=venue.id))

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error = false
  try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
        flash('Venue ' + str(venue.name) + ' successfully deleted.')

  except():
      db.session.rollback()
      flash('An error occurred. Venue ' + str(venue.name) + ' could not be deleted.')
      error = True
  finally:
      db.session.close()
  if error:
      abort(500)
  else:
      return render_template('pages/home.html')

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = db.session.query(Artist).all()
  data = []
  for artist in artists:
    data.append({
      'id':artist.id,
      'name':artist.name,
      })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  artists = db.session.query(Artist).filter(Artist.name.ilike('%'+search_term+'%')).all()
  artist_info = []
  for artist in artists:
    artist_info.append({
      "id" : artist.id,
      "name" : artist.name,
    })
  response={
     "count": len(artists),
     "data": artist_info
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist_data = db.session.query(Artist).filter_by(id=artist_id).all()
  data = []
  for artist in artist_data:
    artist_data = []
    u_shows = db.session.query(Show).filter(Show.artist_id==artist.id).filter(Show.start_time>datetime.now()).all()
    p_shows = db.session.query(Show).filter(Show.artist_id==artist.id).filter(Show.start_time<datetime.now()).all()

    upcoming_shows = []
    for show in u_shows:
      venue = db.session.query(Venue).filter(show.venue_id==Venue.id).all()[0]
      upcoming_shows.append({
        "venue_id": venue.id,
        "venue_image_link": venue.image_link,
        "venue_name": venue.name,
        "start_time": str(show.start_time)
      })

    past_shows = []
    for show in p_shows:
      venue = db.session.query(Venue).filter(show.venue_id==Venue.id).all()[0]
      past_shows.append({
        "venue_id": venue.id,
        "venue_image_link": venue.image_link,
        "venue_name": venue.name,
        "start_time": str(show.start_time)
      })

    data.append({
      "id" : artist.id,
      "name": artist.name,
      "genres": artist.genres,
      "city":artist.city,
      "state":artist.state,
      "phone": artist.phone,
      "website": artist.website,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link":artist.image_link,
      "upcoming_shows": upcoming_shows,
      "past_shows": past_shows,
      "past_shows_count": len(db.session.query(Show).filter(Show.artist_id==artist.id).filter(Show.start_time<datetime.now()).all()),
      "upcoming_shows_count": len(db.session.query(Show).filter(Show.artist_id==artist.id).filter(Show.start_time>datetime.now()).all())
  })

  return render_template('pages/show_artist.html', artist=data[0])

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = db.session.query(Artist).filter(Artist.id == artist_id).all()[0]
  form = ArtistForm(obj=artist) #Populate form with artist information
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.filter_by(id=artist_id).first()
  form = ArtistForm(request.form)
  error = False
  try:
    artist.name = form.name.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.genres = form.genres.data
    artist.website = form.website.data
    artist.facebook_link = form.facebook_link.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data
    artist.image_link = form.image_link.data
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully updated!')

  except:
    db.session.rollback()
    flash('Unable to update Artist : ' + request.form['name'] + '!')

    error = True
  finally:
    db.session.close()
  if error:
    abort(500)
  else:
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = db.session.query(Venue).filter(Venue.id == venue_id).all()[0]
  form = VenueForm(obj=venue) 
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.filter_by(id=venue_id).first()
  form = VenueForm(request.form)
  error = False
  try:
    venue.name = form.name.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.phone = form.phone.data
    venue.website = form.website.data
    venue.genres = form.genres.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    venue.image_link = form.image_link.data
    venue.facebook_link = form.facebook_link.data
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully updated!')

  except:
    db.session.rollback()
    print(sys.exc_info())
    error = True
  finally:
    db.session.close()
  if error:
    flash('Unable to update ' + request.form['name'] + '!')
    abort(500)

  else:
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)

  error = False
  try:
    artist = Artist(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      phone = form.phone.data,
      genres = form.genres.data,
      website = form.website.data,
      facebook_link = form.facebook_link.data,
      seeking_venue = form.seeking_venue.data,
      seeking_description = form.seeking_description.data,
      image_link = form.image_link.data
    )
    db.session.add(artist)
    db.session.commit()
    artist_id = artist.id
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    return render_template('pages/home.html')
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return redirect(url_for('show_artist', artist_id=artist_id))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = db.session.query(Show).all()
  data = []
  for show in shows:
    artist_name = db.session.query(Artist).filter(show.artist_id==Artist.id).all()[0].name
    venue_name = db.session.query(Venue).filter(show.venue_id==Venue.id).all()[0].name
    artist_image_link = db.session.query(Artist).filter(show.artist_id==Artist.id).all()[0].image_link
    data.append({
      "venue_id" : show.venue_id,
      "artist_id": show.artist_id,
      "start_time": str(show.start_time),
      "artist_name": artist_name,
      "venue_name": venue_name,
      "artist_image_link": artist_image_link
  })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm(request.form)
  error = False
  try:
    show = Show(
      artist_id = form.artist_id.data,
      venue_id = form.venue_id.data,
      start_time = form.start_time.data,
    )
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')

  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Show could not be listed.')
    return render_template('pages/home.html')
  else:
    return redirect(url_for('shows'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
