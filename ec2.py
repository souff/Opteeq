"""
Part C cf schema
"""
from tools.aws.awsTools import DynamoDB, BucketCounter
from tools.via.via_converter import via_json
import time


def main(region: str, table_name: str, batch_size: int, bucket_in: str, bucket_out: str,
         annotator_names: list) -> None:
    """
    Get all image without annotator from dynamoDB. Generate json via with annotation by batch and
    upload to s3.
    update dynamoDB with annotator name.

    :param region: dynamoDB table region
    :param table_name: dynamoDB table name
    :param batch_size: batch size for via json
    :param bucket_in: bucket with standardised image
    :param bucket_out: bucket where via json are upload
    :param annotator_names: list the name of all the annotator
    """
    table = DynamoDB(region, table_name)
    bucket = BucketCounter(bucket_out, annotator_names)
    if len(key := table.get_keys_annotator("0")) > batch_size:
        for i in range(len(key) // batch_size):
            batch = key[i * batch_size: (i + 1) * batch_size]
            json = via_json(batch, bucket_in)
            annotator = bucket.put_object_annotator(json, f'{int(time.time())}_{i}.json')
            # todo find if it is possible to update all in one
            for key in batch:
                table.update_annotator(key, annotator)


if __name__ == '__main__':
    main("eu-west-3", "opteeq", 2, "dsti-lab-leo", "opteeqout", ["leo", "leo2", "leo3"])
