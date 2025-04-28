import io

def test_upload_photo(client):
    data = {
        "species": "Heron",
        "description": "Tall bird",
        "location": "Riverside Park",
        "photo": (io.BytesIO(b"fake image data"), "photo.jpg"),
    }
    response = client.post("/create", data=data, content_type='multipart/form-data', follow_redirects=True)
    assert response.status_code == 200
    assert b"Heron" in response.data
