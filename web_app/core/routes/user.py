from flask import (
    Blueprint,
    render_template as rt,
    redirect,
    url_for,
    flash,
    request
)
from flask_login import current_user, login_required
from core.models.user import User
from core.models.sightings import Sighting
from core.forms.user_forms import UpdateAccountForm

user = Blueprint("user", __name__)


@user.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.save()
        flash("Your account has been updated!", "success")
        return redirect(url_for("user.account"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    # Get user's sightings
    user_sightings = current_user.get_sightings()
    return rt(
        "user/profile.html",
        title="Account",
        form=form,
        sightings=user_sightings["items"],
    )


@user.route("/user/<username>")
def user_sightings(username):
    page = request.args.get("page", 1, type=int)
    # user lookup
    user = User.get_by_username(username)
    if not user:
        flash("User not found", "danger")
        return redirect(url_for("main.home"))
    sightings = Sighting.get_by_user_id(user.id, page=page)
    return rt(
        "user/user_sightings.html",
        title=f"{username}'s Sightings",
        sightings=sightings,
        user=user,
    )
