from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, SubmitField, FloatField, HiddenField, IntegerField
from wtforms.validators import DataRequired, Length, Optional, NumberRange


class SightingForm(FlaskForm):
    # species = StringField("Species", validators=[DataRequired(), Length(min=2, max=30)])
    description = TextAreaField(
        "Description (Optional)", validators=[Optional(), Length(max=200)]
    )
    # This line is dead code rn but if we want to add an option
    # that lets the user add a place name then we can add it back
    # in-- but i figure that can just be done in the description
    location_name = StringField(
        "Location Name", validators=[Optional(), Length(min=2, max=50)]
    )
    latitude = FloatField(
        "Latitude", validators=[DataRequired(), NumberRange(min=-90, max=90)]
    )
    longitude = FloatField(
        "Longitude", validators=[DataRequired(), NumberRange(min=-180, max=180)]
    )
    photo = FileField("Upload Image")

    machine_prediction = StringField("Machine Prediction:")
    machine_confidence = IntegerField("Machine Confidence:")

    species_guess = StringField("Issues with the automatic classification? Enter your species guess here or enter \"unknown\":", validators=[Optional(), Length(min=2, max=50)])
    correction_confidence = IntegerField("Rate confidence in your correction (1 (low) -5 (high))", validators=[Optional(), NumberRange(min=1, max=5)])
    submit = SubmitField("Submit")

    # this constructor seems unnecessary but there are
    # a lot of issues with uploading photos without it
    def __init__(self, require_photo=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # right now there is no video allowed, can update this list of valid extensions
        # if we choose to allow video which we probably should at some point
        if require_photo:
            self.photo.validators = [
                FileRequired(),
                FileAllowed(["jpg", "jpeg", "png", "heic", "heif"]),
            ]
        else:
            self.photo.validators = [
                Optional(),
                FileAllowed(["jpg", "jpeg", "png", "heic", "heif"]),
            ]

class ViewsForm(FlaskForm):
    species_guess = StringField("Species doesn't look right? Enter a correction here:", validators=[Optional(), Length(min=2, max=50)])
    correction_confidence = IntegerField("Rate confidence in your correction (1 (low) -5 (high))", validators=[Optional(), NumberRange(min=1, max=5)])
    submit = SubmitField("Submit")