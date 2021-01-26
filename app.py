# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import logging
from logging import FileHandler, Formatter

import babel
import dateutil.parser
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_migrate import Migrate
from flask_moment import Moment

from forms import *
from models import Artist, Show, Venue, db

# App Config.


app = Flask(__name__)

moment = Moment(app)
app.config.from_object("config")
db.init_app(app)
migration = Migrate(app, db)


# Filters.


def format_datetime(value, format="medium"):
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters["datetime"] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route("/")
def index():
    return render_template("/pages/home.html")


#  Venues
#  ----------------------------------------------------------------
@app.route("/venues")
def venues():

    cities = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state)
    data = []
    for city in cities:
        venues_name_id = db.session.query(Venue.id, Venue.name).filter(
            Venue.city == city[0], Venue.state == city[1]
        )
        data.append({"city": city[0], "state": city[1], "venues": venues_name_id})

    return render_template("pages/venues.html", areas=data)


@app.route("/venues/search", methods=["POST"])
def search_venues():

    search_term = request.form.get("search_term", "").strip()
    search = "%{}%".format(search_term)
    venues = Venue.query.filter(Venue.name.ilike(search)).all()

    venues_names = [i.name for i in venues]
    response = {"count": len(venues_names), "data": venues}

    return render_template(
        "pages/search_venues.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)
    # venue = Venue.query.filter(Venue.id == venue_id).one()
    list_shows = (
        db.session.query(Show).join(Artist).filter(Show.venue_id == venue_id).all()
    )
    # (
    #     db.session.query(Show.start_time, Show.artist_id)
    #     .filter(Show.venue_id == venue_id)
    #     .all()
    # )

    past_shows_list = []
    upcoming_shows_list = []
    for show in list_shows:
        artist = (
            db.session.query(Artist.name, Artist.image_link)
            .filter(Artist.id == show.artist_id)
            .one()
        )
        # SQL requests are expensive
        show_data = {
            "artist_id": show.artist_id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y"),
        }

        if show.start_time < datetime.now():

            past_shows_list.append(show_data)
        else:
            upcoming_shows_list.append(show_data)

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows_list,
        "upcoming_shows": upcoming_shows_list,
        "past_shows_count": len(past_shows_list),
        "upcoming_shows_count": len(upcoming_shows_list),
    }
    return render_template("pages/show_venue.html", venue=data)


#  Create Venue
#  ----------------------------------------------------------------


@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
    form = VenueForm(request.form)

    venue = Venue()

    try:
        form.populate_obj(venue)
        db.session.add(venue)
        db.session.commit()
        flash("Venue " + form.name.data + " was successfully listed in the syste,!")
    except:
        flash(
            "An error occurred. Unfortunately Venue "
            + form.name.data
            + " could not be added."
        )
    finally:
        db.session.close()
    return render_template("pages/home.html")


#  Delete Venue
#  ----------------------------------------------------------------


@app.route("/delete/<int:venue_id>", methods=["POST"])
def delete_venue(venue_id):

    try:
        venue = Venue.query.filter(Venue.id == venue_id).one()
        # first delet the shows
        shows = Show.query.filter(Venue.id == venue_id).all()

        for show in shows:
            db.session.delete(show)
            db.session.commit()

        db.session.delete(venue)
        db.session.commit()
        flash("Venue was succesfullly deleted with the shows")

    except ValueError:
        flash("It was not possible to delete this Venue")
        db.session.rollback()

    finally:
        db.session.close()

    return render_template("pages/home.html")


#  Artists
#  ----------------------------------------------------------------
@app.route("/artists")
def artists():
    artists = db.session.query(Artist.id, Artist.name)
    return render_template("pages/artists.html", artists=artists)


@app.route("/artists/search", methods=["POST"])
def search_artists():
    search_term = request.form.get("search_term", "").strip()
    search = "%{}%".format(search_term)
    artists = Artist.query.filter(Artist.name.like(search)).all()

    artists_names = [i.name for i in artists]
    response = {"count": len(artists_names), "data": artists}
    return render_template(
        "pages/search_artists.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):

    artist = Artist.query.filter(Artist.id == artist_id).one()
    list_shows = (
        db.session.query(Show).join(Artist).filter(Show.artist_id == artist_id).all()
    )
    past_shows = []
    upcoming_shows = []

    for show in list_shows:
        venue = (
            db.session.query(Venue.name, Venue.image_link)
            .filter(Venue.id == show.venue_id)
            .one()
        )
        show_add = {
            "venue_id": show.venue_id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": show.start_time.strftime("%m/%d/%Y"),
        }

        if show.start_time < datetime.now():
            past_shows.append(show_add)
        else:
            upcoming_shows.append(show_add)

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }

    return render_template("pages/show_artist.html", artist=data)


#  Update
#  ----------------------------------------------------------------


@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
    artist = Artist.query.filter_by(id=artist_id).one()
    form = ArtistForm(obj=artist)
    return render_template("forms/edit_artist.html", form=form, artist=artist)


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    form = ArtistForm(request.form)

    try:
        new_artist = {
            "name": form.name.data,
            "genres": form.genres.data,
            "city": form.city.data,
            "state": form.state.data,
            "phone": form.phone.data,
            "website": form.website.data,
            "facebook_link": form.facebook_link.data,
            "seeking_venue": form.seeking_venue.data,
            "seeking_description": form.seeking_description.data,
            "image_link": form.image_link.data,
        }

        db.session.query(Artist).filter(Artist.id == artist_id).update(new_artist)
        db.session.commit()
        flash("Artist " + form.name.data + " was successfully listed in the system!")
    except:
        flash(
            "An error occurred. Artist "
            + form.name.data
            + "could not be added in the system"
        )
    finally:
        db.session.close()
    return redirect(url_for("show_artist", artist_id=artist_id))


@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
    form = VenueForm()
    venue = db.session.query(Venue).filter(Venue.id == venue_id).first()
    return render_template("forms/edit_venue.html", form=form, venue=venue)


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
    form = VenueForm(request.form)

    updated_venue = {
        "name": form.name.data,
        "genres": form.genres.data,
        "address": form.address.data,
        "city": form.city.data,
        "state": form.state.data,
        "phone": form.phone.data,
        "website": form.website.data,
        "facebook_link": form.facebook_link.data,
        "seeking_talent": form.seeking_talent.data,
        "seeking_description": form.seeking_description.data,
        "image_link": form.image_link.data,
    }
    try:
        # requires dictionairy as an input
        db.session.query(Venue).filter(Venue.id == venue_id).update(updated_venue)
        db.session.commit()
        flash("Venue" + form.name.data + " was successfully updated!")
    except:
        flash("An error occurred. Venue " + form.name.data + " could not be updated.")
    finally:
        db.session.close()

    return redirect(url_for("show_venue", venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------


@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():

    form = ArtistForm(request.form)

    try:
        artist = Artist()
        form.populate_obj(artist)
        db.session.add(artist)
        db.session.commit()
        flash("Artist " + form.name.data + " was successfully listed!")
    except:
        flash("An error occurred. Artist " + form.name.data + "could not be added")
    finally:
        db.session.close()
    return render_template("pages/home.html")


#  Shows
#  ----------------------------------------------------------------


@app.route("/shows")
def shows():
    data = []
    all_shows = db.session.query(Show.artist_id, Show.venue_id, Show.start_time).all()
    # all_shows = Show.query.all()

    for show in all_shows:
        artist = (
            db.session.query(Artist.name, Artist.image_link)
            .filter(Artist.id == show.artist_id)
            .one()
        )
        venue = db.session.query(Venue.name).filter(Venue.id == show.venue_id).one()
        data.append(
            {
                "venue_id": show.venue_id,
                "venue_name": venue.name,
                "artist_id": show.artist_id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": str(show.start_time),
            }
        )
    return render_template("pages/shows.html", shows=data)


@app.route("/shows/create")
def create_shows():
    # renders form. do not touch.
    form = ShowForm(request.form)
    return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():

    form = ShowForm(request.form)

    try:
        show = Show()
        form.populate_obj(show)
        db.session.add(show)
        db.session.commit()
        flash("Show " " was successfully listed!")
    except:
        flash("An error occurred. Show could not be added")
    finally:
        db.session.close()

    return render_template("pages/home.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == "__main__":
    app.run()

# Or specify port manually:
"""
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
"""
