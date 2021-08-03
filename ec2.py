from tools.aws.awsTools import DynamoDB, Bucket
from tools.via.via_converter import via_json
import time


def main(region: str, table_name: str, batch_size: int, bucket_in: str, bucket_out: str) -> None:
    """
    Get all image without annotator from dynamoDB. Genrate json via with annotation by batch and
    upload to s3.

    todo
    update dynamoDB with annotator name

    :param region: dynamoDB table region
    :param table_name: dynamoDB table name
    :param batch_size: batch size for via json
    :param bucket_in: bucket with standardised image
    :param bucket_out: bucket where via json are upload
    """
    table = DynamoDB(region, table_name)
    bucket = Bucket(bucket_out)
    if len(key := table.get_keys_annotator("0")) > batch_size:
        for i in range(len(key) // batch_size):
            batch = key[i * batch_size: (i + 1) * batch_size]
            json = via_json(batch, bucket_in)
            bucket.put_object(json, f'{int(time.time())}_{i}.json')


if __name__ == '__main__':
    main("eu-west-3", "opteeq", 2, "dsti-lab-leo", "opteeqout")
