from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["genghis-pond"]
collection = db["sightings"]
result = collection.delete_many({})
print(f"Deleted {result.deleted_count} sightings.")
