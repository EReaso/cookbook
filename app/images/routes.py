from flask import send_file, request

from . import bp
from app.extensions import storage


@bp.get("/images/<string:filename>/")
def get_image(filename):
	return send_file(storage.read(filename), mimetype="image/jpeg")


@bp.post("/images/")
def post_image():
	file = request.files["file"]
	return storage.create(file)
