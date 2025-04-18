from flask import Blueprint, render_template as rt

main = Blueprint("main", __name__)


@main.route("/")
@main.route("/home")
def home():
    return rt("index.html", title="Home")


@main.route("/about")
def about():
    return rt("about.html", title="About")
