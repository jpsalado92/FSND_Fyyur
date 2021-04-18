# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import logging
import sys
from logging import Formatter, FileHandler

import babel
import dateutil.parser
from flask import Flask, render_template, request, flash, redirect, url_for, abort
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from models import Venue, Artist, Show

from forms import *

# ----------------------------------------------------------------------------#
# App Config
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


# ----------------------------------------------------------------------------#
# Filters
# ----------------------------------------------------------------------------#

def format_datetime(value, f='medium'):
    date = dateutil.parser.parse(value)
    if f == 'full':
        date_format = "EEEE MMMM, d, y 'at' h:mma"
    elif f == 'medium':
        date_format = "EE MM, dd, y h:mma"
    else:
        date_format = "EE MM, dd"
    return babel.dates.format_datetime(date, date_format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


# ----------------------------------------------------------------------------#
# Venues
# ----------------------------------------------------------------------------#
@app.route('/venues')
def venues():
    data = []
    for state, in db.session.query(Venue.state).distinct().all():
        for _, city in db.session.query(Venue.state, Venue.city).filter(Venue.state == state).distinct().all():
            city_venues = []
            for v_id, v_name, _, _ in db.session.query(Venue.id, Venue.name, Venue.state, Venue.city).filter(
                    Venue.state == state).filter(Venue.city == city).all():
                city_venues.append(
                    {"id": v_id,
                     "name": v_name}
                )
            data.append({
                "city": city,
                "state": state,
                "venues": city_venues
            })
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    data = []
    query = request.form.get('search_term', '')
    for venue in Venue.query.filter(Venue.name.ilike(f'%{query}%')).all():
        data.append({
            "id": venue.id,
            "name": venue.name
        })
    response = {
        "count": len(data),
        "data": data
    }
    return render_template('pages/search_venues.html',
                           results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    venue = Venue.query.filter_by(id=venue_id).first()
    current_time = datetime.utcnow()
    upcoming_shows = []
    for show in Show.query.filter_by(venue_id=venue_id).filter(Show.date >= current_time).all():
        artist = Artist.query.get(show.artist_id)
        upcoming_shows.append({
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": str(show.date)
        })
    past_shows = []
    for show in Show.query.filter_by(venue_id=venue_id).filter(Show.date < current_time).all():
        artist = Artist.query.get(show.artist_id)
        past_shows.append({
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": str(show.date)
        })
    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres[1:-1].split(','),
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "image_link": venue.image_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }
    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # called upon submitting the new artist listing form
    form = VenueForm(request.form)
    if not form.validate():
        print(form.errors.items())
        abort(400)
    else:
        error = False
        try:
            venue = Venue(
                name=form.name.data,
                address=form.address.data,
                city=form.city.data,
                state=form.state.data,
                phone=form.phone.data,
                genres=form.genres.data,
                facebook_link=form.facebook_link.data,
                image_link=form.image_link.data,
                website=form.website.data,
                seeking_talent=form.seeking_talent.data,
                seeking_description=form.seeking_description.data,
            )
            db.session.add(venue)
            db.session.commit()
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
        if error:
            flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
            abort(400)
        else:
            flash('Venue ' + form.name.data + ' was successfully edited!')
    return render_template('pages/home.html')


#  Delete Venue
#  ----------------------------------------------------------------

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    error = False
    try:
        Venue.query.get(venue_id).delete()
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Venue with id ' + venue_id + ' could not be deleted.')
        abort(400)
    else:
        flash('Venue with id ' + venue_id + ' was successfully deleted!')
    return render_template('pages/home.html')


#  Edit Venue
#  ----------------------------------------------------------------

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.filter_by(id=venue_id).first()
    form = VenueForm()
    form.name.default = venue.name
    form.genres.default = venue.genres[1:-1].split(',')
    form.city.default = venue.city
    form.address.default = venue.address
    form.state.default = venue.state
    form.phone.default = venue.phone
    form.seeking_talent.default = venue.seeking_talent
    form.seeking_description.default = venue.seeking_description
    form.website.default = venue.website
    form.image_link.default = venue.image_link
    form.facebook_link.default = venue.facebook_link
    form.process()
    venue = {"id": venue_id, "name": venue.name}
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    form = VenueForm(request.form)
    if not form.validate():
        print(form.errors.items())
        abort(400)
    else:
        error = False
        try:
            venue = Venue.query.get(venue_id)
            venue.name = form.name.data
            venue.city = form.city.data
            venue.address = form.address.data
            venue.state = form.state.data
            venue.phone = form.phone.data
            venue.genres = form.genres.data
            venue.facebook_link = form.facebook_link.data
            venue.image_link = form.image_link.data
            venue.website = form.website.data
            venue.seeking_talent = form.seeking_talent.data
            venue.seeking_description = form.seeking_description.data
            db.session.commit()
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
        if error:
            abort(400)
        else:
            flash('Venue ' + form.name.data + ' was successfully edited!')
            return redirect(url_for('show_venue', venue_id=venue_id))


# ----------------------------------------------------------------------------#
# Artists
# ----------------------------------------------------------------------------#
@app.route('/artists')
def artists():
    data = []
    for artist in Artist.query.order_by(Artist.name).all():
        data.append({"id": artist.id, "name": artist.name})
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    data = []
    query = request.form.get('search_term', '')
    for artist in Artist.query.filter(Artist.name.ilike(f'%{query}%')).all():
        data.append({
            "id": artist.id,
            "name": artist.name,
        })
    response = {
        "count": len(data),
        "data": data
    }
    return render_template('pages/search_artists.html',
                           results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.filter_by(id=artist_id).first()
    current_time = datetime.utcnow()
    upcoming_shows = []
    for show in Show.query.filter_by(artist_id=artist_id).filter(Show.date >= current_time).all():
        venue = Venue.query.get(show.venue_id)
        upcoming_shows.append({
            "venue_id": venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": str(show.date)
        })
    past_shows = []
    for show in Show.query.filter_by(artist_id=artist_id).filter(Show.date < current_time).all():
        venue = Venue.query.get(show.venue_id)
        past_shows.append({
            "venue_id": venue.id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": str(show.date)
        })
    # shows the artist page with the given artist_id
    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres[1:-1].split(','),
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "image_link": artist.image_link,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }
    return render_template('pages/show_artist.html', artist=data)


#  Create Artist
#  ----------------------------------------------------------------
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    form = ArtistForm(request.form)
    if not form.validate():
        print(form.errors.items())
        abort(400)
    else:
        error = False
        try:
            artist = Artist(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                phone=form.phone.data,
                genres=form.genres.data,
                facebook_link=form.facebook_link.data,
                image_link=form.image_link.data,
                website=form.website.data,
                seeking_venue=form.seeking_venue.data,
                seeking_description=form.seeking_description.data,
            )
            db.session.add(artist)
            db.session.commit()
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
        if error:
            flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
            abort(400)
        else:
            flash('Artist ' + form.name.data + ' was successfully listed!')
        return render_template('pages/home.html')


#  Edit Artist
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.filter_by(id=artist_id).first()
    form = ArtistForm()
    form.name.default = artist.name
    form.genres.default = artist.genres[1:-1].split(',')
    form.city.default = artist.city
    form.state.default = artist.state
    form.phone.default = artist.phone
    form.seeking_venue.default = artist.seeking_venue
    form.seeking_description.default = artist.seeking_description
    form.website.default = artist.website
    form.image_link.default = artist.image_link
    form.facebook_link.default = artist.facebook_link
    form.process()
    artist = {"id": artist_id, "name": artist.name}
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    form = ArtistForm(request.form)
    if not form.validate():
        print(form.errors.items())
        abort(400)
    else:
        error = False
        try:
            artist = Artist.query.get(artist_id)
            artist.name = form.name.data
            artist.city = form.city.data
            artist.state = form.state.data
            artist.phone = form.phone.data
            artist.genres = form.genres.data
            artist.facebook_link = form.facebook_link.data
            artist.image_link = form.image_link.data
            artist.website = form.website.data
            artist.seeking_venue = form.seeking_venue.data
            artist.seeking_description = form.seeking_description.data
            db.session.commit()
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
        if error:
            abort(400)
        else:
            flash('Artist ' + form.name.data + ' was successfully edited!')
            return redirect(url_for('show_artist', artist_id=artist_id))


# ----------------------------------------------------------------------------#
# Shows
# ----------------------------------------------------------------------------#
@app.route('/shows')
def shows():
    data = []
    for show in Show.query.order_by(Show.date).all():
        data.append({
            "venue_id": show.venue_id,
            "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
            "artist_id": show.artist_id,
            "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
            "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
            "start_time": str(show.date)
        })
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create', methods=['GET'])
def create_shows_form():
    form = ShowForm()
    form.artist_id.choices = [a_id for a_id, in db.session.query(Artist.id).distinct().all()]
    form.venue_id.choices = [v_id for v_id, in db.session.query(Venue.id).distinct().all()]
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    form = ShowForm(request.form)
    form.artist_id.choices = [a_id for a_id, in db.session.query(Artist.id).distinct().all()]
    form.venue_id.choices = [v_id for v_id, in db.session.query(Venue.id).distinct().all()]
    if not form.validate():
        print(form.errors.items())
        abort(400)
    else:
        error = False
        try:
            show = Show(
                name=form.name.data,
                artist_id=form.artist_id.data,
                venue_id=form.venue_id.data,
                date=form.start_time.data,
            )
            db.session.add(show)
            db.session.commit()
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
        if error:
            flash('An error occurred. Show ' + form.name.data + ' could not be listed.')
            abort(400)
        else:
            flash('Show ' + form.name.data + ' was successfully listed!')
        return render_template('pages/home.html')


# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#
@app.errorhandler(404)
def not_found_error():
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error():
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

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
