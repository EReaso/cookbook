import os
import uuid
from pathlib import Path
from typing import Optional, Union


class Storage:
	dir: Path
	"""Abstract class for storing data in a bucket."""

	def __init__(self, dir: Optional[Union[str, Path]] = None):
		# Don't require an app at construction time. If a dir is provided,
		# prepare it now; otherwise final initialization happens in init_app().
		self.dir = Path(dir) if dir is not None else None
		if self.dir is not None and not self.dir.exists():
			os.makedirs(self.dir)

	def init_app(self, app=None, dir: Optional[Union[str, Path]] = None):
		"""Finish initialization using a Flask app or an explicit directory.

		If `app` is provided, its `instance_path` is used (unless `dir` is
		provided). This method is safe to call multiple times.

		Returns the Storage instance (self).
		"""
		chosen_dir = None
		if dir is not None:
			chosen_dir = Path(dir)
		elif app is not None:
			chosen_dir = Path(app.instance_path)

		if chosen_dir is None:
			raise ValueError("must provide app or dir to initialize storage")

		self.dir = chosen_dir
		if not self.dir.exists():
			os.makedirs(self.dir)

		# Standard Flask pattern: register on app.extensions if app provided
		if app is not None:
			if not hasattr(app, "extensions"):
				app.extensions = {}
			app.extensions["storage"] = self

		return self

	def create(self, file) -> str:
		"""Store a file and return its UUID string key.

		Accepts a werkzeug FileStorage-like object (has .read()) or raw bytes.
		Requires that `init_app` has previously been called (or a dir was
		provided at construction).
		"""
		if self.dir is None:
			raise RuntimeError("storage not initialized; call init_app(app) or provide dir")

		# Read bytes from FileStorage or accept bytes directly
		if hasattr(file, "read"):
			data = file.read()
		else:
			data = file

		file_uuid = uuid.uuid4()
		file_path = self.dir / str(file_uuid)
		with file_path.open("wb") as f:
			f.write(data)
		return str(file_uuid)

	def read(self, key) -> Path:
		"""Return the Path to the stored file for the given key.

		Raises RuntimeError if storage not initialized. Caller is responsible
		for checking existence or handling FileNotFound as appropriate.
		"""
		if self.dir is None:
			raise RuntimeError("storage not initialized; call init_app(app) or provide dir")
		return self.dir / key

	def update(self, filename, new_value):
		# Optional: implement overwrite behavior
		p = self.dir / filename
		with p.open("wb") as f:
			f.write(new_value)

	def delete(self, filename):
		if self.dir is None:
			return
		p = self.dir / filename
		if p.exists():
			p.unlink()

	# convenience magic methods
	def __iadd__(self, file):
		return self.create(file)

	def __getitem__(self, item):
		return self.read(item)

	def __delitem__(self, item):
		self.delete(item)
