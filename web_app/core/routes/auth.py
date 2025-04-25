from core.forms.auth_forms import LoginForm, RegistrationForm
from core.models.user import User
from flask import Blueprint, flash, redirect
from flask import render_template as rt
from flask import request, url_for
from flask_login import current_user, login_user, logout_user

auth = Blueprint("auth", __name__)


# Login page
@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_email(form.email.data)
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("main.home"))
        else:
            flash("Login unsuccessful!!! Please check email and password", "danger")
    return rt("auth/login.html", title="Login", form=form)


# Create account
@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data, email=form.email.data, password_hash=None
        )
        user.set_password(form.password.data)
        user.save()
        flash(
            f"Account created for {form.username.data}! You can now log in.", "success"
        )
        return redirect(url_for("auth.login"))
    return rt("auth/register.html", title="Register", form=form)


@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.home"))
