import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "duck"
    MONGO_URI = os.environ.get("MONGO_URI") or "mongodb://mongodb:27017/genghis-pond"
    # File upload configuration
    UPLOAD_FOLDER = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "static/uploads"
    )
    # Up tp 16mb uploads allowed for the time being
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    # Can also change this if we decide to allow uploading videos?
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "heic", "heif"}
    # Map API configuration
    MAP_API_KEY = os.environ.get("MAP_API_KEY") or ""

    # S3 configuration
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME", "genghis-pond")
    AWS_S3_REGION_NAME = os.environ.get("AWS_S3_REGION_NAME", "us-east-2")
