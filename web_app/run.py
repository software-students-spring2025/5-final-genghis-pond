from core import create_app, mongo

app = create_app()

with app.app_context():
    # Create a 2dsphere index for geospatial queries :O
    mongo.db.sightings.create_index([("location", "2dsphere")])
    # Create text index for species search
    mongo.db.sightings.create_index([("species", "text")])
    # Create indexes for common queries
    mongo.db.users.create_index([("username", 1)], unique=True)
    mongo.db.users.create_index([("email", 1)], unique=True)
    mongo.db.sightings.create_index([("user_id", 1)])
    mongo.db.sightings.create_index([("date_posted", -1)])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
