from app.book import bp
from flask import render_template, request, redirect, url_for
from app.extensions import db


@bp.route("/book/")
def book():
    return render_template("bookview.html")
