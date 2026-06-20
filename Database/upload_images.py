import json
import re
import urllib.request
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

REGION = "us-east-1"
JSON_FILE = "2026a2_songs.json"
BUCKET_NAME = "118group-music-images"
S3_PREFIX = "artist-images/"

s3 = boto3.client("s3", region_name=REGION)


def load_json_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    songs = data.get("songs", [])

    if not isinstance(songs, list):
        raise ValueError("Invalid JSON format: 'songs' must be a list.")

    return songs


def safe_artist_filename(artist):
    safe_name = artist.strip().lower()
    safe_name = re.sub(r"[^a-z0-9]+", "_", safe_name)
    safe_name = safe_name.strip("_")
    return f"{safe_name}.jpg"


def object_exists(bucket_name, object_key):
    try:
        s3.head_object(Bucket=bucket_name, Key=object_key)
        return True

    except ClientError as error:
        error_code = error.response["Error"]["Code"]

        if error_code in ["404", "NoSuchKey", "NotFound"]:
            return False

        raise


def upload_file_to_s3(file_path, bucket_name, object_key):
    s3.upload_file(
        Filename=str(file_path),
        Bucket=bucket_name,
        Key=object_key,
        ExtraArgs={"ContentType": "image/jpeg"}
    )


def main():
    songs = load_json_file(JSON_FILE)

    artist_to_url = {}

    for song in songs:
        artist = str(song["artist"]).strip()
        img_url = str(song["img_url"]).strip()

        if artist not in artist_to_url:
            artist_to_url[artist] = img_url

    temp_dir = Path.home() / "temp_artist_images"
    temp_dir.mkdir(exist_ok=True)

    uploaded_count = 0
    skipped_count = 0
    error_count = 0

    for artist, img_url in artist_to_url.items():
        filename = safe_artist_filename(artist)
        object_key = f"{S3_PREFIX}{filename}"
        temp_file = temp_dir / filename

        try:
            if object_exists(BUCKET_NAME, object_key):
                skipped_count += 1
                print(f"Skipped existing image: {object_key}")
                continue

            urllib.request.urlretrieve(img_url, temp_file)

            upload_file_to_s3(
                file_path=temp_file,
                bucket_name=BUCKET_NAME,
                object_key=object_key
            )

            uploaded_count += 1
            print(f"Uploaded {artist}: s3://{BUCKET_NAME}/{object_key}")

        except Exception as error:
            error_count += 1
            print(f"Error processing {artist}: {error}")

        finally:
            if temp_file.exists():
                temp_file.unlink()

    print("\nUpload complete.")
    print(f"Uploaded: {uploaded_count}")
    print(f"Skipped existing: {skipped_count}")
    print(f"Errors: {error_count}")


if __name__ == "__main__":
    main()