import os
import uuid6
from pathlib import Path


class Storage:
	dir: Path
	"""Abstract class for storing data in a bucket."""

	def __init__(self, dir):
		"""Initialize the storage in a directory.

		:param dir: The absolute path of the directory to store the data in."""
		self.dir = Path(dir)
		if not self.dir.exists():
			os.makedirs(self.dir)

	def create(self, file) -> str:
		"""Create a new file entry in the bucket.

		:param value: The file to store in the bucket.
		:return: The UUID to retreive the file."""

		file_uuid = uuid6.uuid7()
		file_path = self.dir / str(file_uuid)
		with file_path.open('wb') as f:
			f.write(file)
		return str(file_uuid)

	def read(self, key):
		"""Retrieve a file from the bucket.

		:param key: UUID of the file to retrieve.
		:return: The file path, which can be opened with open()."""
		return self.dir / key

	def update(self, filename, new_value):
		"""Update a file in the bucket.

		:param filename: The file to store in the bucket.
		:param new_value: The new value to store in the bucket.
		:return: None"""
		pass

	def delete(self, filename):
		"""Delete a file from the bucket.

		:param filename: The file to store in the bucket."""
