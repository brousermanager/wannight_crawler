import pandas as pd
from .utils import download_image_from_s3, compress_image, downloadImageFromWeb, upload_image_to_s3, delete_image_from_s3, bucket_name


def image_uploader(url_image, id, bucket_name):
    """Uploads an image to the specified bucket.

    Args:
        url_image (_type_): _description_
        id (_type_): _description_
        bucket_name (_type_): _description_

    Returns:
        _type_: _description_
    """
    try:
        input_bytes = downloadImageFromWeb(url_image)
        compressed_image = compress_image(input_bytes)
        upload_image_to_s3(compressed_image, id+'.jpg', bucket_name)
        print('uploaded')
        return True
    # if everything is ok, return True and you can actually save as a flag in the database that the image has been uploaded
    except Exception as e:
        print(e)
        return False


def image_downloader(event_id, bucket_name=bucket_name):
    """Download image.

    Args:
        event_id (_type_): _description_
        bucket_name (_type_, optional): _description_. Defaults to BUCKET_NAME.

    Returns:
        _type_: _description_
    """
    try:
        image_bytes = download_image_from_s3(event_id+'.jpg')
        return image_bytes
    except Exception as e:
        print(e)
        return None


def image_deleter(event_id, bucket_name=bucket_name):
    """Delete image.

    Args:
        event_id (_type_): _description_
        bucket_name (_type_, optional): _description_. Defaults to BUCKET_NAME.

    Returns:
        _type_: _description_
    """
    try:
        delete_image_from_s3(event_id+'.jpg')
        return True
    except Exception as e:
        print(e)
        return False


# run this query and dowload as csv
# SELECT id_fb
# FROM wannight.evento
# WHERE data_inizio < CURRENT_DATE;

def delete_all_past_images():
    """Delete all images in the csv.

    Returns:
        _type_: _description_
    """
    try:
        df = pd.read_csv('past_events.csv')
        for i in range(len(df)):
            print(df['id_fb'][i])
            string_id = str(df['id_fb'][i])
            image_deleter(string_id+'.jpg')
        return True
    except Exception as e:
        print(e)

    return True
