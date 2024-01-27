import boto3
from PIL import Image
import requests
import io
import os

bucket_name = os.environ.get('BUCKET_NAME')



def upload_image_to_s3(image_content, key_name, bucket_name):
    """Upload image to s3 bucket.

    Args:
        image_content (bytes): image content in bytes
        key_name (str): name of the image es. test.jpg
        bucket_name (set): _description_
    """

    # set up S3 client
    s3 = boto3.client('s3', aws_access_key_id=os.environ.get(
        'AWS_ACCESS_KEY_ID'), aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))

    # upload file to S3
    s3.upload_fileobj(io.BytesIO(image_content), bucket_name, key_name)


def download_image_from_s3(key_name):
    """Download image from s3 bucket. 
    Esempio: key_name: 'test.jpg'

    Args:
        key_name (str): name of the image to be downloaded

    Returns:
        _type_: _description_
    """
    # set up S3 client
    try:
        s3 = boto3.client('s3', aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                          aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))

        # download file from S3
        bucket_name = os.environ.get('BUCKET_NAME')
        obj = s3.get_object(Bucket=bucket_name, Key=key_name)
        content = obj['Body'].read()
        return content
    except Exception as e:
        print(e)
        return None


def delete_image_from_s3(key_name, bucket_name=bucket_name):
    """Delete image from s3 bucket.

    Args:
        key_name (str): _description_
        bucket_name (str, optional): _description_. Defaults to BUCKET_NAME.

    Returns:
        _type_: _description_
    """

    # set up S3 client
    try:
        s3 = boto3.client('s3', aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                          aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))

        # delete file from S3
        s3.delete_object(Bucket=bucket_name, Key=key_name)
        # TODO: qui ci andrebbe una return True tipo
        print('deleted')
    except Exception as e:
        print(e)
        return None


# downloadImageFromWeb()
def downloadImageFromWeb(link):
    """Download image from web
    Esempio: link: 'https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png'

    Args:
        link (str): link of the image to download

    Returns:
        bytes: return the contents of the get request
    """
    try:
        r = requests.get(link)
        return r.content
    except Exception as e:
        print(e)
        return None


def compress_image(image_bytes, max_size=512):
    """Compresses an image in bytes to meet Telegram's image size limits. 

    Args:
        image_bytes (bytes): image to compress
        max_size (int): kilobytes maximum size

    Returns:
        output_bytes (bytes): Returns the compressed image
    """
    # Open the image from bytes
    image = Image.open(io.BytesIO(image_bytes))

    # Reduce the image size while maintaining the aspect ratio
    width, height = image.size
    if width > height:
        new_width = max_size
        new_height = int(height * max_size / width)
    else:
        new_height = max_size
        new_width = int(width * max_size / height)
    resized_image = image.resize((new_width, new_height))

    # Convert the image to JPEG format with 80% quality
    output = io.BytesIO()
    resized_image.save(output, format='JPEG', quality=80)
    output_bytes = output.getvalue()

    # Check if the compressed image is still too large
    if len(output_bytes) > max_size * 1024:
        raise ValueError(
            "Compressed image size exceeds the maximum allowed size")

    return output_bytes
