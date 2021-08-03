import boto3
from boto3.dynamodb.conditions import Key
import logging
from botocore.exceptions import ClientError
import os
import json
from typing import Union


class Bucket:
    def __init__(self, bucket_name):
        self.client = boto3.resource("s3").Bucket(bucket_name)

    def upload(self, file_path: str, object_name: str = None) -> None:
        """
        Upload a file to Bucket

        :param file_path: path of the file to upload
        :param object_name: S3 object name. If not specified then file_name is used
        """
        if object_name is None:
            object_name = os.path.basename(file_path)
        try:
            self.client.upload_file(file_path, object_name)
        except ClientError as e:
            logging.error(e)

    def put_object(self, content: Union[str, dict, int, float], key: str) -> None:
        """
        Function to upload python variable in s3.

        Convert dict in json and other python variable in string, convert in bytes and upload to s3.

        :param content: python variable to upload
        :param key: key for s3 object
        """
        if isinstance(content, dict):
            content = json.dumps(content)
        else:
            content = str(content)
        self.client.put_object(Body=bytes(content.encode("UTF-8")), Key=key)

    def download(self, key: str, file_path: str) -> None:
        """
        Download a file from Bucket

        :param key: object key
        :param file_path: destination path
        """
        self.client.download_file(key, file_path)

    def read(self, key: str) -> bytes:
        """
        load in memory object from s3.

        :param key: object key
        :return: object bytes
        """
        return self.client.Object(key).get()["Body"].read()


class DynamoDB:
    def __init__(self, region, table_name):
        self.client = boto3.resource('dynamodb', region_name=region).Table(table_name)

    def query(self, **kwargs) -> dict:
        """
        Dynamodb query.

        :param kwargs: all possible kwargs for query cf dynamo db doc.
        :return: query result
        """
        return self.client.query(**kwargs)

    def query_index_eq(self, index: str, key_name: str, value: str) -> dict:
        """
        Query on a secondary index equal value

        :param index: index name
        :param key_name: key name
        :param value: key value
        :return: query result
        """
        return self.query(IndexName=index, KeyConditionExpression=Key(key_name).eq(value))

    def get_keys_annotator(self, annotator: str) -> list:
        """
        Query on the annotator index and get all the key of standardised image.

        :param annotator: annotator name value
        :return: list all key of standardised image with the given annotator.
        """
        items = self.query_index_eq("annotator-index", "annotator", annotator)["Items"]
        return [i["standardised"] for i in items]

    def update(self, **kwargs) -> Union[dict, None, Exception]:
        """
        DynamoDB update

        :param kwargs: all possible kwargs dynamoDB update cf docs
        :return: response or exception
        """
        try:
            response = self.client.update_item(**kwargs)
        except ClientError as e:
            if e.response['Error']['Code'] == "ConditionalCheckFailedException":
                print(e.response['Error']['Message'])
            else:
                raise
        else:
            return response

    def update_annotator(self, key: str, annotator: str) -> None:
        """
        Update the annotator value of the given key.

        :param key: primary key value
        :param annotator: new annotator name
        """
        return self.update(Key={'standardised': key},
                           UpdateExpression="set annotator=:a",
                           ExpressionAttributeValues={
                               ':a': annotator,
                           },
                           ReturnValues="UPDATED_NEW")
