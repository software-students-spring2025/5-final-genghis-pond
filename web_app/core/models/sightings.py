import math
import typing
from math import asin, cos, radians, sin, sqrt

from bson.objectid import ObjectId
from pymongo import ASCENDING, DESCENDING

from .. import mongo

if typing.TYPE_CHECKING:
    from core.models.user import User


class Sighting:
    def __init__(self, **kwargs):
        self._id = kwargs.get("_id")
        self.species = kwargs.get("species")
        # this does nothing atm
        self.location_name = kwargs.get("location_name")
        self.latitude = kwargs.get("latitude")
        self.longitude = kwargs.get("longitude")
        self.user_id = kwargs.get("user_id")
        self.description = kwargs.get("description")
        self.image_file = kwargs.get("image_file")
        self.date_posted = kwargs.get("date_posted")
        self.crit = kwargs.get("crit")

    @property
    def id(self):
        return str(self._id)

    def get_distance(self, user_lat, user_lng):
        # radius of the earth
        radius = 6371
        # I got these calculations online i don't remember any trig idk how this works
        dlat = radians(float(self.latitude) - float(user_lat))
        dlon = radians(float(self.longitude) - float(user_lng))
        a = (
            sin(dlat / 2) ** 2
            + cos(radians(float(user_lat)))
            * cos(radians(float(self.latitude)))
            * sin(dlon / 2) ** 2
        )
        c = 2 * asin(sqrt(a))
        return round(radius * c, 2)

    def get_votes(self):
        all_votes = list(mongo.db.votes.find({"sighting_id": self.id}))
        if len(all_votes) == 0:
            return None
        species_votes = {}
        vote_num = len(all_votes)
        vote_sum = 0  # sum of confidence weighted votes
        for vote in all_votes:
            if vote.get("species_guess") not in species_votes:
                species_votes[vote.get("species_guess")] = 0
            species_votes[vote.get("species_guess")] += vote.get("confidence_level", 1)
            vote_sum += vote.get("confidence_level", 1)
        sorted_species = {
            k: round(100 * float(v) / vote_sum, 2)
            for k, v in sorted(
                species_votes.items(), key=lambda item: item[1], reverse=True
            )
        }
        return sorted_species, vote_num

    @classmethod
    def get_by_id(cls, sighting_id):
        from bson.errors import InvalidId

        try:
            object_id = ObjectId(sighting_id)
        except InvalidId:
            print("Invalid ObjectId:", sighting_id)
            return None
        # query mongodb
        sighting_data = mongo.db.sightings.find_one({"_id": object_id})
        if not sighting_data:
            print("No sighting found with _id:", object_id)
            return None
        try:
            allowed_fields = {
                "species",
                "location_name",
                "latitude",
                "longitude",
                "user_id",
                "description",
                "image_file",
                "date_posted",
                "_id",
            }
            clean_data = {k: v for k, v in sighting_data.items() if k in allowed_fields}
            return cls(**clean_data)
        except Exception as e:
            print("Error constructing Sighting object:", e)
            return None

    @classmethod
    def get_all(cls, page=1, per_page=10, sort_by="date_posted", sort_order=-1):
        sort_field = sort_by
        skip = (page - 1) * per_page
        direction = DESCENDING if sort_order == -1 else ASCENDING
        # Get total count
        total = mongo.db.sightings.count_documents({"crit": 0})
        # Breaks results down into pages
        cursor = (
            mongo.db.sightings.find({"crit": 0})
            .sort(sort_field, direction)
            .skip(skip)
            .limit(per_page)
        )
        # Create page object
        items = [
            cls(**{k: v for k, v in doc.items() if k != "location"}) for doc in cursor
        ]
        return {
            "items": items,
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": math.ceil(total / per_page),
        }

    @classmethod
    def search(
        cls, species=None, page=1, per_page=10, sort_by="date_posted", sort_order=-1
    ):
        search_query = {}
        # add a regex line here eventually when adding search by species
        total = mongo.db.sightings.count_documents(search_query)
        direction = DESCENDING if sort_order == -1 else ASCENDING
        skip = (page - 1) * per_page
        cursor = (
            mongo.db.sightings.find(search_query)
            .sort(sort_by, direction)
            .skip(skip)
            .limit(per_page)
        )
        allowed_fields = {
            "species",
            "location_name",
            "latitude",
            "longitude",
            "user_id",
            "description",
            "image_file",
            "date_posted",
            "_id",
        }
        items = [
            cls(**{k: v for k, v in doc.items() if k in allowed_fields})
            for doc in cursor
        ]
        return {
            "items": items,
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": math.ceil(total / per_page),
            "has_prev": page > 1,
            "has_next": page < math.ceil(total / per_page),
            "iter_pages": cls._get_page_numbers(page, math.ceil(total / per_page)),
        }

    # This just generates buttons for pages once there's a lot for posts
    # this could probably be done on the front end so lmk if I should delete
    @classmethod
    def _get_page_numbers(cls, page, total_pages, edge=1, middle=2):
        if total_pages <= 1:
            return []
        pages = []
        # Add left pages
        for i in range(1, min(edge + 1, total_pages + 1)):
            pages.append(i)
        # Add middle pages around current page
        left = max(page - middle, edge + 1)
        right = min(page + middle, total_pages - edge)
        # Add ellipsis
        if left > edge + 1:
            pages.append(None)
        # Add middle pages
        for i in range(left, min(right + 1, total_pages + 1)):
            pages.append(i)
        if right < total_pages - edge:
            pages.append(None)
        # Add right pages
        for i in range(max(total_pages - edge + 1, right + 1), total_pages + 1):
            pages.append(i)
        return pages

    @classmethod
    def get_by_user_id(cls, user_id, page=1, per_page=10):
        total = mongo.db.sightings.count_documents({"user_id": user_id})
        skip = (page - 1) * per_page
        # make query
        cursor = (
            mongo.db.sightings.find({"user_id": user_id})
            .sort("date_posted", DESCENDING)
            .skip(skip)
            .limit(per_page)
        )
        items = [
            cls(**{k: v for k, v in doc.items() if k != "location"}) for doc in cursor
        ]
        return {
            "items": items,
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": math.ceil(total / per_page),
            "has_prev": page > 1,
            "has_next": page < math.ceil(total / per_page),
            "iter_pages": cls._get_page_numbers(page, math.ceil(total / per_page)),
        }

    # Allows you to search near a geographic area
    @classmethod
    def search_near(cls, lat, lng, max_distance=10000, page=1, per_page=10):
        # geospatial query
        query = {
            "location": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [float(lng), float(lat)],
                    },
                    "$maxDistance": max_distance,
                }
            }
        }
        total = mongo.db.sightings.count_documents(query)
        skip = (page - 1) * per_page
        cursor = mongo.db.sightings.find(query).skip(skip).limit(per_page)
        items = [cls(**doc) for doc in cursor]
        return {
            "items": items,
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": math.ceil(total / per_page),
        }

    def save(self):
        sighting_data = {
            "species": self.species,
            "description": self.description,
            # again this line does nothing atm
            "location_name": self.location_name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "user_id": self.user_id,
            "image_file": self.image_file,
            "date_posted": self.date_posted,
            "location": {
                "type": "Point",
                "coordinates": [self.longitude, self.latitude],
            },
            "crit": self.crit,
        }
        if self._id:
            mongo.db.sightings.update_one({"_id": self._id}, {"$set": sighting_data})
        else:
            result = mongo.db.sightings.insert_one(sighting_data)
            self._id = result.inserted_id
        return self

    @property
    def author(self):
        return User.get_by_id(self.user_id)

    # returns all the sightings and creates a geoJSON file sigma
    # not sure entirely how this works got from tutorial
    @classmethod
    def get_all_as_geojson(cls):
        cursor = mongo.db.sightings.find()
        features = []
        for doc in cursor:
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [doc["longitude"], doc["latitude"]],
                },
                "properties": {
                    "id": str(doc["_id"]),
                    "species": doc["species"],
                    "location_name": doc["location_name"],
                    "date": doc["date_posted"].strftime("%Y-%m-%d"),
                    "has_image": bool(doc.get("image_file")),
                },
            }
            if doc.get("image_file"):
                feature["properties"]["image_file"] = doc["image_file"]
            features.append(feature)
        return {"type": "FeatureCollection", "features": features}

    def delete(self):
        if self._id:
            mongo.db.sightings.delete_one({"_id": ObjectId(str(self._id))})
            return True
        return False
