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


def download_image(bucket, key):
    """
    Returns an object (i.e., image) in the specified s3 bucket. Checks if it exists first.
    :param bucket: S3 bucket object
    :param key: Image name, including any prefix (i.e., path) to the bucket root. Example: 'docs/en/doggo.png'
    :return: File object
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


def upload_image(bucket, image_path, key):
    """
    Uploads a file to your S3 bucket.
    :param bucket: S3 bucket object
    :param image_path: Local path to the image file. Can be a pathlib object
    :param key: Name of the file in the bucket, including the virtual path. Example: 'docs/fr/doggo.png'
    :return: None
    """
    bucket.upload_file(str(image_path), Key=key, ExtraArgs={'ACL': 'public-read'})
