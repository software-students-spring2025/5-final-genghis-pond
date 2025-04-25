from bson.objectid import ObjectId
from core import bcrypt, login_manager, mongo
from core.models.sightings import Sighting
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


class User(UserMixin):
    def __init__(self, username, email, password_hash, _id=None):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self._id = _id

    @property
    def id(self):
        return str(self._id)

    @classmethod
    def get_by_id(cls, user_id):
        try:
            user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
            if user_data:
                return cls(**user_data)
            return None
        except Exception:
            return None

    @classmethod
    def get_by_email(cls, email):
        user_data = mongo.db.users.find_one({"email": email})
        if user_data:
            return cls(**user_data)
        return None

    @classmethod
    def get_by_username(cls, username):
        user_data = mongo.db.users.find_one({"username": username})
        if user_data:
            return cls(**user_data)
        return None

    def save(self):
        if self._id:
            mongo.db.users.update_one(
                {"_id": self._id},
                {
                    "$set": {
                        "username": self.username,
                        "email": self.email,
                        "password_hash": self.password_hash,
                    }
                },
            )
        else:
            result = mongo.db.users.insert_one(
                {
                    "username": self.username,
                    "email": self.email,
                    "password_hash": self.password_hash,
                }
            )
            self._id = result.inserted_id
        return self

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def get_sightings(self):
        return Sighting.get_by_user_id(self.id)
