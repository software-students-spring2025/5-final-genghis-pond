# I'm not sure in which directory to put this file. Should we make a utils directory?
import boto3
from botocore.exceptions import NoCredentialsError
from flask import current_app


def upload_file_to_s3(file_data, content_type=None, filename=None):
    # Configure S3 client
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=current_app.config["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=current_app.config["AWS_SECRET_ACCESS_KEY"],
        region_name=current_app.config["AWS_S3_REGION_NAME"],
    )
    try:
        # Set content type if necessary
        extra_args = {}
        if content_type:
            extra_args["ContentType"] = content_type
        # Upload
        s3_client.upload_fileobj(
            file_data,
            current_app.config["AWS_STORAGE_BUCKET_NAME"],
            filename,
            ExtraArgs=extra_args,
        )
        # Generate the URL
        url = f"https://{current_app.config['AWS_STORAGE_BUCKET_NAME']}.s3.{current_app.config['AWS_S3_REGION_NAME']}.amazonaws.com/{filename}"
        return url
    except NoCredentialsError:
        current_app.logger.error("AWS credentials not available")
        return None
    except Exception as e:
        # Handle other errors
        current_app.logger.error(f"Error uploading to S3: {str(e)}")
        return None
