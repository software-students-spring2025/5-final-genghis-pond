def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome" in response.data

def test_create_sighting_page(client):
    response = client.get("/create")
    assert response.status_code == 200
    assert b"Submit Sighting" in response.data

def test_create_sighting_post(client):
    data = {
        "species": "Duck",
        "description": "Saw a duck at the pond.",
        "location": "Central Park"
    }
    response = client.post("/create", data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Duck" in response.data
