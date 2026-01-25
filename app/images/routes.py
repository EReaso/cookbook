from flask import abort, request, send_file

import app.extensions as extensions

from . import bp


@bp.get("/<path:filename>")
def get_image(filename):
    # Access the storage from the module so we read the runtime-assigned value
    storage = extensions.storage
    if storage is None:
        abort(500, "storage not initialized")
    file_path = storage.read(filename)
    if not file_path.exists():
        abort(404)
    return send_file(file_path, mimetype="image/jpeg")


@bp.post("/")
def post_image():
    file = request.files.get("file")
    if not file:
        abort(400, "no file uploaded")
    storage = extensions.storage
    if storage is None:
        abort(500, "storage not initialized")
    return storage.create(file)
