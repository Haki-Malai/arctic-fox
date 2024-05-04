import os
import boto3
from flask import Flask
from dotenv import load_dotenv
from colorthief import ColorThief
from io import BytesIO

from typing import List, Dict, Any, Optional


class AWSWrapper:

    def __init__(self) -> None:
        self.initialized = False

    def init_app(self, app: Flask):
        """Initialize the AWSWrapper with app configuration.

        :param app: The Flask application instance.
        """
        self.aws_bucket = app.config['AWS_BUCKET']
        self.s3_client = boto3.client(
            's3', aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'],
            region_name=app.config['AWS_REGION'])
        self.rekognition_client = boto3.client(
            'rekognition', aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'],
            region_name=app.config['AWS_REGION'])
        self.initialized = True

    def ping_s3_bucket(self) -> None:
        """Ping S3 bucket.

        :return: None if successful, otherwise an error description."""
        self.s3_client.list_objects_v2(Bucket=self.aws_bucket, MaxKeys=1)

    def upload_file_object_to_s3(self, folder: str, file_object: object,
                                 s3_key: str) -> None:
        """Uploads a file-like object to an S3 bucket.

        :param file_object: A file-like object to upload.
        :param s3_key: The S3 key (filename) where the file will be stored.

        :return: None if successful, otherwise an error description.
        """
        if folder:
            s3_key = f'{folder}/{s3_key}'

        self.s3_client.upload_fileobj(file_object, self.aws_bucket, s3_key)

    def list_uploaded_files(self) -> list:
        """List files in the S3 bucket.

        :return: List of files if successful, otherwise an error description.
        """
        response = self.s3_client.list_objects_v2(Bucket=self.aws_bucket)
        files = []
        if 'Contents' in response:
            files = [content['Key'] for content in response['Contents']]
            return files

    def upload_file_to_s3(self, file_path: str, s3_key: str) -> None:
        """Upload a file to S3.

        :param local_file_path: The local file path.
        """
        with open(file_path, 'rb') as f:
            self.s3_client.upload_fileobj(f, self.aws_bucket, s3_key)

    def generate_dominant_color(self, s3_key: str) -> Optional[str]:
        """Generate the dominant color of an image stored in S3. Supports both raster images and SVGs.

        :param s3_key: The S3 key (filename) where the image is stored.
        :return: The dominant color as a hex string. If error, returns None.
        """
        try:
            response = self.get_s3_object(s3_key)
            if response is None or 'Body' not in response:
                return None

            image_bytes = response['Body'].read()
            image_stream = BytesIO(image_bytes)

            color_thief = ColorThief(image_stream)
            dominant_color = color_thief.get_color(quality=1)

            return '#{:02x}{:02x}{:02x}'.format(*dominant_color)
        except Exception as e:
            print(f'Error generating dominant color: {e}')
            return None

    def delete_file_from_s3(self, s3_key: str) -> None:
        """Delete a file from S3.

        :param s3_key: The S3 key (filename) where the file is stored.
        """
        self.s3_client.delete_object(Bucket=self.aws_bucket, Key=s3_key)

    def generate_presigned_url(self, s3_key: str, expiration: int=3600) -> Optional[str]:
        """Generate a presigned URL to share an S3 object.

        :param s3_key: The name of the object to share.
        :param expiration: Time in seconds for the presigned URL to remain valid.
        :return: Presigned URL as string. If error, returns None.
        """
        return self.s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.aws_bucket, 'Key': s3_key},
            ExpiresIn=expiration
        )

    def get_s3_object(self, s3_key: str) -> Optional[Dict]:
        """Fetch an object from S3 using the bucket and key.

        :param s3_key: The S3 key (filename) where the file is stored.
        :return: The fetched object if successful, otherwise an error description.
        """
        return self.s3_client.get_object(Bucket=self.aws_bucket, Key=s3_key)

    def generate_image_labels(self, s3_key: str, max_labels: int=10,
                              min_confidence: float=75.0) -> Optional[List]:
        """Generate labels for an image stored in S3 using Amazon Rekognition.

        :param s3_key: The S3 key (filename) where the image is stored.
        :param max_labels: Maximum number of labels to return.
        :param min_confidence: Minimum confidence level for returned labels.

        :return: List of label data if successful, otherwise None.
        """
        if not hasattr(self, 'rekognition_client'):
            self._init_rekognition_client()

        response = self.rekognition_client.detect_labels(
            Image={
                'S3Object': {
                    'Bucket': self.aws_bucket,
                    'Name': s3_key
                }
            },
            MaxLabels=max_labels,
            MinConfidence=min_confidence
        )

        return response.get('Labels', [])

    def generate_presigned_post(self, filename: str, fields=None, conditions=None, folder: str=None,
                                expiration=3600) -> Optional[Dict[str, Any]]:
        """Generate a presigned URL S3 POST request to upload a file.

        :param folder: Folder in the S3 bucket where the file will be uploaded.
        :param filename: Name of the file to upload.
        :param fields: Fields to include in the presigned POST.
        :param conditions: Conditions to include in the presigned POST.
        :param expiration: Time in seconds for the presigned POST to remain valid.

        :return: Presigned POST data if successful, otherwise None.
        """
        s3_key = f'{folder}/{filename}' if folder else filename

        presigned_post = self.s3_client.generate_presigned_post(
            Bucket=self.aws_bucket, Key=s3_key, Fields=fields, Conditions=conditions,
            ExpiresIn=expiration)

        return presigned_post
    
    def clean_s3_bucket(self) -> None:
        """Delete all items (objects) from the S3 bucket."""
        files = self.list_uploaded_files()
        for file_key in files:
            self.delete_file_from_s3(file_key)

        print('S3 bucket cleaned successfully.')


if __name__ == '__main__':
    load_dotenv()

    fake_config = {
        'AWS_ACCESS_KEY_ID': os.getenv('AWS_ACCESS_KEY_ID'),
        'AWS_SECRET_ACCESS_KEY': os.getenv('AWS_SECRET_ACCESS_KEY'),
        'AWS_REGION': os.getenv('AWS_REGION'),
        'AWS_BUCKET': os.getenv('AWS_BUCKET')
    }
    app = Flask(__name__)
    app.config = fake_config

    aws = AWSWrapper()
    aws.init_app(app)

    print(aws.clean_s3_bucket())
