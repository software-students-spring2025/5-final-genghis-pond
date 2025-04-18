import os
import secrets
from PIL import Image
from flask import (
    Blueprint,
    render_template as rt,
    redirect,
    url_for,
    flash,
    request,
    current_app,
    jsonify,
)
from flask_login import current_user, login_required
from core.models.sightings import Sighting
from core.forms.sightings_forms import SightingForm
from core import csrf
from math import radians, cos, sin, asin, sqrt
from datetime import datetime

sightings = Blueprint("sightings", __name__)


def save_image(form_image):
    # assigns a random name to the image when uploaded
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_image.filename)
    image_filename = random_hex + f_ext
    image_path = os.path.join(current_app.root_path, "static/uploads", image_filename)
    # Resizes the image with max dimension 800 x 8000
    output_size = (800, 800)
    i = Image.open(form_image)
    i.thumbnail(output_size)
    i.save(image_path)
    return image_filename


# again I'm not sure how this trig works exactly got this online
def haversine(lat1, lon1, lat2, lon2):
    radius = 6371
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    )
    c = 2 * asin(sqrt(a))
    return radius * c


# lists all sightings
@sightings.route("/sightings")
def list_view():
    user_lat = request.args.get("user_lat", type=float)
    user_lng = request.args.get("user_lng", type=float)
    # might not be a long term sustainable way to sort if there's thousands of posts
    sightings_data = Sighting.get_all()
    sightings = sightings_data["items"]
    if user_lat is not None and user_lng is not None:
        sightings.sort(
            key=lambda s: haversine(user_lat, user_lng, s.latitude, s.longitude)
        )
    return rt(
        "sightings/list.html",
        title="Wildlife Sightings",
        sightings=sightings,
        filter=None,
        sort_by=None,
    )


@sightings.route("/sightings/map")
def map_view():
    geojson = Sighting.get_all_as_geojson()
    return rt(
        "sightings/map.html", sightings_json=geojson, user_lat=40.0, user_lng=-74.0
    )


@sightings.route("/sightings/api/data")
def sightings_data():
    sightings_geojson = Sighting.get_all_as_geojson()
    return jsonify(sightings_geojson)


# view a single post/sighting
@sightings.route("/sightings/<sighting_id>")
def view_sighting(sighting_id):
    sighting = Sighting.get_by_id(sighting_id)
    if not sighting:
        flash("Sighting not found", "danger")
        return redirect(url_for("sightings.list_view"))
    return rt(
        "sightings/view.html", title=f"{sighting.species} Sighting", sighting=sighting
    )


@sightings.route("/sightings/new", methods=["GET", "POST"])
@login_required
def create_sighting():
    # instantiate form
    form = SightingForm(require_photo=True)
    if form.validate_on_submit():
        # deals with image saving
        image_file = None
        if form.photo.data:
            image_file = save_image(form.photo.data)
        # create sighting object
        sighting = Sighting(
            species=form.species.data,
            description=form.description.data,
            date_posted=datetime.utcnow(),
            location_name=form.location_name.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            user_id=current_user.id,
            image_file=image_file,
        )
        sighting.save()
        flash("Your wildlife sighting has been posted!", "success")
        return redirect(url_for("sightings.view_sighting", sighting_id=sighting.id))
    return rt(
        "sightings/create.html",
        title="New Sighting",
        form=form,
        legend="Report Wildlife Sighting",
    )


@sightings.route("/sightings/<sighting_id>/edit", methods=["GET", "POST"])
@login_required
def edit_sighting(sighting_id):
    sighting = Sighting.get_by_id(sighting_id)
    # permission checking
    if not sighting or sighting.user_id != current_user.id:
        flash("You don't have permission to edit this sighting.", "danger")
        return redirect(url_for("main.home"))
    form = SightingForm(require_photo=False)
    if form.validate_on_submit():
        sighting.species = form.species.data
        sighting.description = form.description.data
        sighting.location_name = form.location_name.data
        sighting.latitude = form.latitude.data
        sighting.longitude = form.longitude.data
        if form.photo.data:
            image_file = save_image(form.photo.data)
            sighting.image_file = image_file
        sighting.save()
        flash("Sighting updated!", "success")
        return redirect(url_for("sightings.view_sighting", sighting_id=sighting.id))
    # Pre-fill form on GET might want to extarct
    # this logic from this function as a helper
    form.species.data = sighting.species
    form.description.data = sighting.description
    form.location_name.data = sighting.location_name
    form.latitude.data = sighting.latitude
    form.longitude.data = sighting.longitude
    return rt(
        "sightings/create.html",
        title="Edit Sighting",
        form=form,
        legend="Edit Sighting",
        sighting=sighting,
    )


@csrf.exempt
@sightings.route("/sightings/<sighting_id>/delete", methods=["POST"])
@login_required
def delete_sighting(sighting_id):
    sighting = Sighting.get_by_id(sighting_id)
    if not sighting or sighting.user_id != current_user.id:
        flash("You don’t have permission to delete this sighting!", "danger")
        return redirect(url_for("main.home"))
    sighting.delete()
    flash("Sighting deleted.", "success")
    return redirect(url_for("main.home"))
