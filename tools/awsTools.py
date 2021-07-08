import boto3
import logging
from botocore.exceptions import ClientError
import os


class Bucket:
    def __init__(self, bucket_name):
        self.client = boto3.resource("s3").Bucket(bucket_name)

    def upload(self, file_path: str, object_name: str = None):
        """Upload a file to Bucket

        :param file_path: path of the file to upload
        :param object_name: S3 object name. If not specified then file_name is used
        """
        if object_name is None:
            object_name = os.path.basename(file_path)
        try:
            self.client.upload_file(file_path, object_name)
        except ClientError as e:
            logging.error(e)

    def download(self, key: str, file_path: str):
        """Download a file frm Bucket

        :param key: object key
        :param file_path: destination path
        """
        self.client.download_file(key, file_path)
