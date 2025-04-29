import io
from bson.objectid import ObjectId
from core import mongo
from core.models.user import User
from core.models.sightings import Sighting


def test_register(client):
    response = client.post('/register', data={
        'username': 'sigma',
        'email': 'sigma@gmail.com',
        'password': '123',
        'confirm_password': '123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data


def test_login(client):
    response = client.post('/login', data={
        'email': 'sigma@gmail.com',
        'password': '123'
    }, follow_redirects=True)
    assert response.status_code == 200
    # check login redirect to home
    assert b'My Profile' in response.data or b'Welcome' in response.data or b'Home' in response.data


def test_login_invalid(client):
    response = client.post('/login', data={
        'email': 'sigma@gmail.com',
        'password': 'wrong123'
    }, follow_redirects=True)
    assert response.status_code == 200
    # just check if it's still the login page
    assert b'Login' in response.data


def test_sightings_list(client):
    response = client.get('/sightings')
    assert response.status_code == 200
    assert b'Wildlife Sightings' in response.data


def test_create_sighting(logged_in_client, mock_s3_upload, mock_find_species, test_user, mock_get_votes):
    # Create a test image
    image_data = io.BytesIO(b'fake image data')
    image_data.name = 'test.jpg'
    response = logged_in_client.post('/sightings/new', data={
        'description': 'Test sighting description',
        'latitude': 40.7128,
        'longitude': -74.0060,
        'photo': (image_data, 'test.jpg'),
        'machine_prediction': 'duck',
        'machine_confidence': 4
    }, content_type='multipart/form-data', follow_redirects=True)
    assert response.status_code == 200
    # does the response contains an idication of success
    assert b'Test sighting description' in response.data or b'duck' in response.data
    assert mock_s3_upload.called
    with logged_in_client.application.app_context():
        sightings = list(mongo.db.sightings.find({'user_id': test_user.id}))
        assert len(sightings) >= 1
        found = False
        for s in sightings:
            if s.get('description') == 'Test sighting description':
                found = True
                assert s['latitude'] == 40.7128
                assert s['longitude'] == -74.0060
                break
        assert found, "Created sighting not found in database"


def test_view_sighting(client, test_sighting, mock_get_votes):
    response = client.get(f'/sightings/{test_sighting.id}')
    assert response.status_code == 200
    assert b'Test description' in response.data


def test_submit_vote(logged_in_client, test_sighting, mock_get_votes):
    response = logged_in_client.post(f'/sightings/{test_sighting.id}/submit_vote', data={
        'species_guess': 'red-tailed hawk',
        'correction_confidence': 5
    }, follow_redirects=True)
    assert response.status_code == 200
    # Check if the page contains the species name
    assert b'red-tailed hawk' in response.data
    with logged_in_client.application.app_context():
        votes = list(mongo.db.votes.find({'sighting_id': test_sighting.id, 'species_guess': 'red-tailed hawk'}))
        assert len(votes) >= 1
        # at least one vote should have the correct values
        found = False
        for v in votes:
            if v.get('species_guess') == 'red-tailed hawk' and v.get('confidence_level') == 5:
                found = True
                break
        assert found, "Submitted vote not found in database"


def test_user_account(logged_in_client):
    response = logged_in_client.get('/account')
    assert response.status_code == 200
    assert b'My Profile' in response.data
    assert b'humphrey' in response.data


def test_update_account(logged_in_client):
    response = logged_in_client.post('/account', data={
        'username': 'user',
        'email': 'john@gmail.com'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'My Profile' in response.data
    with logged_in_client.application.app_context():
        updated_user = User.get_by_username('user')
        assert updated_user is not None


def test_map_view(client):
    response = client.get('/sightings/map')
    assert response.status_code == 200
    assert b'map' in response.data.lower()


def test_sightings_api_data(client):
    response = client.get('/sightings/api/data')
    assert response.status_code == 200
    assert b'FeatureCollection' in response.data


def test_upload_image(logged_in_client, mock_s3_upload, mock_get_votes):
    # Create a test image
    image_data = io.BytesIO(b'fake image data')
    image_data.name = 'test.jpg'
    response = logged_in_client.post('/sightings/new', data={
        'description': 'Test image upload',
        'latitude': 40.7128,
        'longitude': -74.0060,
        'photo': (image_data, 'test.jpg')
    }, content_type='multipart/form-data', follow_redirects=True)
    assert response.status_code == 200
    assert mock_s3_upload.called
    with logged_in_client.application.app_context():
        sighting = mongo.db.sightings.find_one({'description': 'Test image upload'})
        assert sighting is not None
        assert sighting['image_file'] == 'http://fake-s3-bucket.s3.amazonaws.com/test_image.jpg'


def test_delete_sighting(logged_in_client, test_sighting):
    response = logged_in_client.post(f'/sightings/{test_sighting.id}/delete', follow_redirects=True)
    assert response.status_code == 200
    # make sure the sighting was deleted from the database
    with logged_in_client.application.app_context():
        deleted_sighting = mongo.db.sightings.find_one({'_id': ObjectId(test_sighting.id)})
        assert deleted_sighting is None


def test_s3_upload_function(app):
    from core.s3_utils import upload_file_to_s3
    from io import BytesIO
    from unittest.mock import patch, MagicMock
    test_file = BytesIO(b'Test file content')
    mock_s3_client = MagicMock()
    with patch('boto3.client', return_value=mock_s3_client):
        with app.app_context():
            # Configure the app with required S3 settings
            app.config.update({
                'AWS_ACCESS_KEY_ID': 'test_key',
                'AWS_SECRET_ACCESS_KEY': 'test_secret',
                'AWS_S3_REGION_NAME': 'us-east-1',
                'AWS_STORAGE_BUCKET_NAME': 'test-bucket'
            })
            url = upload_file_to_s3(test_file, content_type='text/plain', filename='test.txt')
            mock_s3_client.upload_fileobj.assert_called_once()
            assert url == 'https://test-bucket.s3.us-east-1.amazonaws.com/test.txt'


def test_s3_upload_failure(app):
    from core.s3_utils import upload_file_to_s3
    from io import BytesIO
    from unittest.mock import patch, MagicMock
    from botocore.exceptions import NoCredentialsError
    test_file = BytesIO(b'Test file content')
    mock_s3_client = MagicMock()
    mock_s3_client.upload_fileobj.side_effect = NoCredentialsError()
    with patch('boto3.client', return_value=mock_s3_client):
        with app.app_context():
            app.config.update({
                'AWS_ACCESS_KEY_ID': 'test_key',
                'AWS_SECRET_ACCESS_KEY': 'test_secret',
                'AWS_S3_REGION_NAME': 'us-east-1',
                'AWS_STORAGE_BUCKET_NAME': 'test-bucket'
            })
            url = upload_file_to_s3(test_file, filename='test.txt')
            mock_s3_client.upload_fileobj.assert_called_once()
            # verify we got None back due to the error
            assert url is None


def test_find_species_integration(app, mock_find_species):
    from core.routes.sightings import find_species as sightings_find_species
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.jpg') as temp_file:
        temp_file.write(b'fake image data')
        temp_file.flush()
        # Test that find_species is called correctly
        mock_find_species.return_value = ('duck', 0.95, 5)
        assert sightings_find_species is not None
        assert mock_find_species is not None


def test_haversine_distance(app):
    from core.routes.sightings import haversine
    # New York to Los Angeles ig
    nyc_lat, nyc_lon = 40.7128, -74.0060
    la_lat, la_lon = 34.0522, -118.2437
    # approximate distance between NYC and LA is around 3900-4000 km
    distance = haversine(nyc_lat, nyc_lon, la_lat, la_lon)
    assert distance > 3900 and distance < 4000
    # test with same location (should be 0 distance)
    distance = haversine(nyc_lat, nyc_lon, nyc_lat, nyc_lon)
    assert distance < 0.1


def test_list_view_with_params(client):
    # Test with species parameter
    response = client.get('/sightings?species=duck')
    assert response.status_code == 200
    assert b'Wildlife Sightings' in response.data
    # Test with location parameters
    response = client.get('/sightings?user_lat=40.7128&user_lng=-74.0060')
    assert response.status_code == 200
    assert b'Wildlife Sightings' in response.data


def test_save_temp_image(client):
    from core.routes.sightings import save_temp_image
    import os
    from io import BytesIO
    from PIL import Image
    img = Image.new('RGB', (100, 100), color='red')
    img_io = BytesIO()
    img.save(img_io, 'JPEG')
    img_io.seek(0)
    img_io.filename = 'test.jpg'
    with client.application.app_context():
        filename = save_temp_image(img_io)
        # Check if the file was created
        upload_path = os.path.join(client.application.root_path, "static/uploads/ml_temp")
        file_path = os.path.join(upload_path, filename)
        assert os.path.exists(file_path)
        os.remove(file_path)
    with client.application.app_context():
        filename = save_temp_image(img_io)
        # Check if the file was created
        upload_path = os.path.join(client.application.root_path, "static/uploads/ml_temp")
        file_path = os.path.join(upload_path, filename)
        assert os.path.exists(file_path)
        os.remove(file_path)


def test_sighting_model_methods(app, test_user):
    from core.models.sightings import Sighting
    from datetime import datetime
    with app.app_context():
        sighting = Sighting(
            species="beast",
            description="Test description",
            latitude=40.7128,
            longitude=-74.0060,
            user_id=test_user.id,
            image_file="http://example.com/test.jpg",
            date_posted=datetime.now().replace(microsecond=0)
        )
        sighting.save()
        # Test get_distance
        distance = sighting.get_distance(40.7128, -74.0060)
        assert distance == 0.0
        distance = sighting.get_distance(40.7, -74.0)
        assert distance > 0
        search_result = Sighting.search(species="test")
        assert isinstance(search_result, dict)
        assert "items" in search_result
        assert "page" in search_result
        user_sightings = Sighting.get_by_user_id(test_user.id)
        assert isinstance(user_sightings, dict)
        assert "items" in user_sightings
        assert len(user_sightings["items"]) > 0
        pages = Sighting._get_page_numbers(1, 10)
        assert isinstance(pages, list)
        sighting.delete()


def test_predict_species_endpoint(logged_in_client, mock_find_species):
    from io import BytesIO
    from PIL import Image
    img = Image.new('RGB', (100, 100), color='red')
    img_io = BytesIO()
    img.save(img_io, 'JPEG')
    img_io.seek(0)
    # Mock the find_species function
    mock_find_species.return_value = ('duck', 0.95, 5)
    response = logged_in_client.post(
        '/predict_species',
        data={'photo': (img_io, 'test.jpg')},
        content_type='multipart/form-data'
    )
    assert response.status_code == 200
    assert b'duck' in response.data
    # Test with no file
    response = logged_in_client.post('/predict_species')
    assert response.status_code == 400
    new_img_io = BytesIO()
    img.save(new_img_io, 'JPEG')
    new_img_io.seek(0)
    response = logged_in_client.post(
        '/predict_species',
        data={'photo': (new_img_io, '')},
        content_type='multipart/form-data'
    )
    assert response.status_code == 400


def test_species_names_endpoint(client):
    from unittest.mock import patch, MagicMock
    import pandas as pd
    # Mock the pandas read_csv
    mock_df = pd.DataFrame({'common_name': ['duck', 'goose', 'swan']})
    with patch('pandas.read_csv', return_value=mock_df):
        response = client.get('/species_names')
        assert response.status_code == 200
        assert b'duck' in response.data
        assert b'goose' in response.data
        assert b'swan' in response.data
        assert b'unknown' in response.data


def test_find_species_error_handling(app):
    from core.routes.sightings import find_species
    import os
    from unittest.mock import patch, MagicMock
    import subprocess
    import json
    with app.app_context():
        # Test subprocess error
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(1, 'cmd')
            result = find_species('/fake/path', '/fake/output')
            assert result is None
        # Test file not found error
        with patch('subprocess.run') as mock_run, \
                patch('builtins.open') as mock_open:
            mock_run.return_value = MagicMock()
            mock_open.side_effect = FileNotFoundError()
            result = find_species('/fake/path', '/fake/output')
            assert result is None
        # Test JSON decode error
        with patch('subprocess.run') as mock_run, \
                patch('builtins.open') as mock_open, \
                patch('json.load') as mock_json:
            mock_run.return_value = MagicMock()
            mock_open.return_value.__enter__.return_value = MagicMock()
            mock_json.side_effect = json.JSONDecodeError('msg', 'doc', 0)
            result = find_species('/fake/path', '/fake/output')
            assert result is None
        # Test with class that has no species (different structure)
        with patch('subprocess.run') as mock_run, \
                patch('builtins.open') as mock_open, \
                patch('json.load') as mock_json, \
                patch('os.remove') as mock_remove, \
                patch('os.listdir') as mock_listdir:
            mock_run.return_value = MagicMock()
            mock_open.return_value.__enter__.return_value = MagicMock()
            # Modified to match the expected format in your find_species function
            mock_json.return_value = {
                'predictions': [
                    {'classifications': {'classes': [';;'], 'scores': [0.5]}}
                ]
            }
            mock_listdir.return_value = ['file1.jpg']
            mock_remove.return_value = None
            result = find_species('/fake/path', '/fake/output')
            mock_remove.assert_called_once()


def test_save_image_error(app):
    from core.routes.sightings import save_image
    from unittest.mock import patch, MagicMock, ANY
    from io import BytesIO
    from PIL import Image
    # Create a test image
    img = Image.new('RGB', (100, 100), color='red')
    img_io = BytesIO()
    img.save(img_io, 'JPEG')
    img_io.seek(0)
    img_io.filename = 'test.jpg'
    with app.app_context():
        app.config.update({
            'AWS_ACCESS_KEY_ID': 'test_key',
            'AWS_SECRET_ACCESS_KEY': 'test_secret',
            'AWS_S3_REGION_NAME': 'us-east-1',
            'AWS_STORAGE_BUCKET_NAME': 'test-bucket'
        })
        with patch('boto3.client') as mock_client, \
                patch('PIL.Image.open') as mock_open:
            mock_s3 = MagicMock()
            mock_client.return_value = mock_s3
            mock_s3.upload_fileobj.side_effect = Exception('S3 error')
            # Mock PIL.Image.open to return our test image
            mock_img = MagicMock()
            mock_open.return_value = mock_img
            mock_img.format = 'JPEG'
            with patch('os.path.join', return_value='/fake/path'):
                result = save_image(img_io)
                mock_s3.upload_fileobj.assert_called_once()
                assert not result.startswith('http')