"""Tests for the Storage class."""
import uuid
from pathlib import Path

import pytest
from app.storage import Storage


class TestStorage:
    """Test suite for Storage class."""

    def test_storage_init_with_dir(self, tmp_path):
        """Test storage initialization with a directory."""
        storage_dir = tmp_path / "storage"
        storage = Storage(dir=storage_dir)
        
        assert storage.dir == storage_dir
        assert storage_dir.exists()

    def test_storage_init_app(self, app, tmp_path):
        """Test storage initialization with Flask app."""
        storage_dir = tmp_path / "test_storage"
        storage = Storage()
        storage.init_app(app, dir=storage_dir)
        
        assert storage.dir == storage_dir
        assert storage_dir.exists()

    def test_storage_create_with_bytes(self, tmp_path):
        """Test creating a file from bytes."""
        storage = Storage(dir=tmp_path)
        test_data = b"test file content"
        
        file_id = storage.create(test_data)
        
        # Check that file_id is a valid UUID
        assert uuid.UUID(file_id)
        
        # Check that file exists and contains correct data
        file_path = tmp_path / file_id
        assert file_path.exists()
        assert file_path.read_bytes() == test_data

    def test_storage_create_with_file_object(self, tmp_path):
        """Test creating a file from a file-like object."""
        storage = Storage(dir=tmp_path)
        
        # Create a mock file object
        class MockFile:
            def read(self):
                return b"mock file content"
        
        mock_file = MockFile()
        file_id = storage.create(mock_file)
        
        # Check that file exists and contains correct data
        file_path = tmp_path / file_id
        assert file_path.exists()
        assert file_path.read_bytes() == b"mock file content"

    def test_storage_read(self, tmp_path):
        """Test reading a file from storage."""
        storage = Storage(dir=tmp_path)
        test_data = b"read test data"
        file_id = storage.create(test_data)
        
        file_path = storage.read(file_id)
        
        assert isinstance(file_path, Path)
        assert file_path.exists()
        assert file_path.read_bytes() == test_data

    def test_storage_update(self, tmp_path):
        """Test updating a file in storage."""
        storage = Storage(dir=tmp_path)
        file_id = storage.create(b"original data")
        
        new_data = b"updated data"
        storage.update(file_id, new_data)
        
        file_path = storage.read(file_id)
        assert file_path.read_bytes() == new_data

    def test_storage_delete(self, tmp_path):
        """Test deleting a file from storage."""
        storage = Storage(dir=tmp_path)
        file_id = storage.create(b"delete me")
        file_path = storage.read(file_id)
        
        assert file_path.exists()
        storage.delete(file_id)
        assert not file_path.exists()

    def test_storage_magic_methods(self, tmp_path):
        """Test storage magic methods."""
        storage = Storage(dir=tmp_path)
        test_data = b"magic test"
        
        # Test __iadd__
        file_id = storage.create(test_data)
        
        # Test __getitem__
        file_path = storage[file_id]
        assert isinstance(file_path, Path)
        assert file_path.read_bytes() == test_data
        
        # Test __delitem__
        del storage[file_id]
        assert not file_path.exists()

    def test_storage_not_initialized_error(self):
        """Test that operations fail when storage is not initialized."""
        storage = Storage()
        
        with pytest.raises(RuntimeError, match="storage not initialized"):
            storage.create(b"test")
        
        with pytest.raises(RuntimeError, match="storage not initialized"):
            storage.read("test-id")
