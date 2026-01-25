"""Tests for image routes."""
import io
import pytest


class TestImageRoutes:
    """Test suite for image routes."""

    def test_post_image(self, client, app):
        """Test uploading an image."""
        # Create a fake image file
        data = {
            'file': (io.BytesIO(b"fake image data"), 'test.jpg')
        }
        
        response = client.post(
            '/images/',
            data=data,
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 200
        # Should return a UUID string
        file_id = response.data.decode('utf-8')
        assert len(file_id) > 0

    def test_post_image_without_file(self, client):
        """Test uploading without a file."""
        response = client.post('/images/')
        assert response.status_code == 400

    def test_get_image(self, client, app):
        """Test retrieving an image."""
        # First upload an image
        data = {
            'file': (io.BytesIO(b"fake image data"), 'test.jpg')
        }
        
        post_response = client.post(
            '/images/',
            data=data,
            content_type='multipart/form-data'
        )
        
        file_id = post_response.data.decode('utf-8')
        
        # Now retrieve it
        response = client.get(f'/images/{file_id}')
        assert response.status_code == 200
        assert response.data == b"fake image data"
        assert response.mimetype == "image/jpeg"

    def test_get_nonexistent_image(self, client):
        """Test retrieving an image that doesn't exist."""
        response = client.get('/images/nonexistent-image-id')
        assert response.status_code == 404
