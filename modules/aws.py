import boto3
from botocore.exceptions import ClientError


def get_s3_bucket(name):
    """
    Returns an s3 bucket.
    :param name: Bucket name. Example: 'zen-marketing-documentation'
    :return: s3 bucket
    """
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(name)
    return bucket


def get_image(bucket, key):
    """
    Returns an object (i.e., image) in the specified s3 bucket. Checks if it exists first.
    :param bucket: s3 bucket
    :param key: Image name, including any prefix (i.e., path) to the bucket root. Example: 'docs/en/doggo.png'
    :return: Object
    """
    try:
        bucket.Object(key).load()
        return bucket.Object(key)
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        else:
            print('- error code {}'.format(e.response['Error']['Code']))   # something other than a 404
            return 'error'
