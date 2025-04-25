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
from core.forms.sightings_forms import ViewsForm
from core.models.vote import Vote
from core import csrf
from math import radians, cos, sin, asin, sqrt
from datetime import datetime
import subprocess
import os
import json
import pandas as pd

sightings = Blueprint("sightings", __name__)


def save_image(form_image):
    # assigns a random name to the image when uploaded
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_image.filename)
    image_filename = random_hex + f_ext
    image_path = os.path.join(current_app.root_path, "static/uploads/", image_filename)
    # Resizes the image with max dimension 800 x 8000
    output_size = (800, 800)
    i = Image.open(form_image)
    i.thumbnail(output_size)
    i.save(image_path)

    return image_filename

def save_temp_image(form_image):
    '''
    temporary folder for ml animal classification
    # probably not a good way to do this
    '''
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_image.filename)
    image_filename = random_hex + f_ext
    upload_path = os.path.join(current_app.root_path, "static/uploads/ml_temp")
    os.makedirs(upload_path, exist_ok=True) # i can't find the folder in github so make sure it exists here
    image_path = os.path.join(upload_path, image_filename)
    # Resizes the image with max dimension 800 x 8000
    output_size = (800, 800)
    i = Image.open(form_image)
    i.thumbnail(output_size)
    i.save(image_path)

    return image_filename # not necessary


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
    form = ViewsForm()
    sighting = Sighting.get_by_id(sighting_id)
    if not sighting:
        flash("Sighting not found", "danger")
        return redirect(url_for("sightings.list_view"))
    
    species_votes = sighting.get_votes()[0]
    vote_num = sighting.get_votes()[1]

    return rt(
        "sightings/view.html", title=f"{sighting.species} Sighting", sighting=sighting,
        form=form, species_votes=species_votes, vote_num=vote_num
    )

@sightings.route("/sightings/<sighting_id>/submit_vote", methods=["POST"])
@login_required
def submit_vote(sighting_id):
    sighting = Sighting.get_by_id(sighting_id)
    if not sighting:
        flash("Sighting not found", "danger")
        return redirect(url_for("sightings.list_view"))
    
    species_guess = request.form.get('species_guess')
    correction_confidence = request.form.get('correction_confidence')

    if not species_guess:
        flash("Please enter a correction species", "warning")
        return redirect(url_for("sightings.view_sighting", sighting_id=sighting_id))

    vote = Vote(
        species_guess=species_guess,
        sighting_id=sighting_id,
        confidence_level=int(correction_confidence) if correction_confidence else 1,
        user_id=current_user.id
    )
    vote.save_vote()

    flash("Thanks for your correction!", "success")
    return redirect(url_for("sightings.view_sighting", sighting_id=sighting_id))


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

        ml_prediction = form.machine_prediction.data
        ml_confidence = form.machine_confidence.data
        
        print("ML PREDICTION: ", ml_prediction)

        print("ML PREDICTION: ", ml_confidence)

        user_prediction = form.species_guess.data
        user_confidence = form.correction_confidence.data
        print("user PREDICTION: ", user_prediction)
        print("user CONFIDENCE: ", user_confidence)

        sighting = Sighting(
            species='unknown',
            description=form.description.data,
            date_posted=datetime.utcnow(),
            location_name=form.location_name.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            user_id=current_user.id,
            image_file=image_file,
        )
        sighting.save()

        if user_prediction and user_confidence:
            user_vote = Vote(
                species_guess = user_prediction,
                sighting_id = sighting.id,
                user_id = sighting.user_id,
                confidence_level = user_confidence
            )
            user_vote.save_vote()

        if ml_prediction and ml_confidence:
            ml_vote = Vote(
                species_guess = ml_prediction,
                sighting_id = sighting.id,
                user_id = 'speciesnet', # i guess speciesnet gets one vote
                confidence_level = ml_confidence
            )
            ml_vote.save_vote()

        flash("Your wildlife sighting has been posted!", "success")
        return redirect(url_for("sightings.view_sighting", sighting_id=sighting.id))
    return rt(
        "sightings/create.html",
        title="New Sighting",
        form=form,
        legend="Report Wildlife Sighting",
    )


@sightings.route("/predict_species", methods=["POST"])
@login_required
def predict_species():
    '''
    Call find_species once a photo is uploaded
    '''
    if 'photo' not in request.files:
        return {'error': 'No file uploaded'}, 400

    file = request.files['photo']
    if file.filename == '':
        return {'error': 'No selected file'}, 400
    
    random_hex = secrets.token_hex(8)
    save_temp_image(file)
    upload_path = os.path.join(current_app.root_path, "static/uploads/ml_temp")
    output_path = os.path.join(current_app.root_path, f"outputs/predictions{random_hex}.json")
    prediction = find_species(upload_path, output_path)
    if prediction:
        species_name, score, confidence = prediction
        print("Predict species: ", prediction)
        return {'species': species_name, 'score': score, 'confidence': confidence}
    else:
        return {'error': 'No species found'}, 400

@sightings.route("/species_names")
def species_names():
    '''
    Pull the 'common_name' column out of full_data.tsv for fuzzy search
    '''
    df_path = os.path.join(current_app.root_path, 'databases/full_data.tsv')
    df = pd.read_csv(df_path, delimiter='\t')
    print(df["common_name"].head())
    names = df['common_name'].dropna().unique().tolist()
    names.append('unknown') # manually input unknown for nonsense predictions
    return jsonify(names)

def find_species(upload_path, output_path):
    """
    Call command line function for speciesnet
    models.yolo not accessible
    """

    try:
        subprocess.run([
            'python', '-m', 'speciesnet.scripts.run_model',
            '--folders', upload_path,
            '--predictions_json', output_path
        ], check=True)

        with open(output_path, 'r', encoding="utf-8") as temp_file:
            predictions_dict = json.load(temp_file)

    except subprocess.CalledProcessError as e:
        print("Subprocess failed:", e)
        return
    except FileNotFoundError:
        print("Prediction file not found.")
        return
    except json.JSONDecodeError:
        print("Prediction file not valid JSON.")
        return

    os.remove(output_path) # remove the json to avoid storage issues? possibly not necessary
    for filename in os.listdir(upload_path): # clear ml_temp
        file_path = os.path.join(upload_path, filename)
        if os.path.isfile(file_path):
            os.remove(file_path) # this is more important than removing the json!!!
    # as is, upload_path should only have ONE image file (the one that is actively being analyzed)

    classes = predictions_dict['predictions'][0]['classifications']['classes']
    scores = predictions_dict['predictions'][0]['classifications']['scores']

    for i, cl in enumerate(classes):
        cl_split = cl.split(';')
        if len(cl_split[-2]) == 0: # indicates no species found
            classes.remove(cl)
            del scores[i]
        else:
            confidence = int(100 * scores[i]/20) + 1 # scale from 1 to 5
            print("Found species ", cl_split[-1])
            return cl_split[-1], scores[i], confidence 
            # assumes sorted in decreasing confidence order


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
