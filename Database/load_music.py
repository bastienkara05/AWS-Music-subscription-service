import json
import boto3
from botocore.exceptions import ClientError

REGION = "us-east-1"
MUSIC_TABLE = "music"
JSON_FILE = "2026a2_songs.json"

dynamodb = boto3.resource("dynamodb", region_name=REGION)
table = dynamodb.Table(MUSIC_TABLE)


def build_title_year(title, year):
    return f"{title}#{year}"


def load_json_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    songs = data.get("songs", [])

    if not isinstance(songs, list):
        raise ValueError("Invalid JSON format: 'songs' must be a list.")

    return songs


def validate_song(song):
    required_fields = ["title", "artist", "year", "album", "img_url"]

    for field in required_fields:
        if field not in song:
            raise ValueError(f"Missing required field: {field}")

    return {
        "title": str(song["title"]).strip(),
        "artist": str(song["artist"]).strip(),
        "year": str(song["year"]).strip(),
        "album": str(song["album"]).strip(),
        "img_url": str(song["img_url"]).strip(),
    }


def insert_song(song):
    title_year = build_title_year(song["title"], song["year"])

    item = {
        "artist": song["artist"],
        "title_year": title_year,
        "title": song["title"],
        "year": song["year"],
        "album": song["album"],
        "img_url": song["img_url"],
    }

    try:
        table.put_item(
            Item=item,
            ConditionExpression="attribute_not_exists(artist) AND attribute_not_exists(title_year)"
        )
        return True

    except ClientError as error:
        if error.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return False
        raise


def main():
    songs = load_json_file(JSON_FILE)

    inserted_count = 0
    skipped_count = 0
    error_count = 0

    for raw_song in songs:
        try:
            song = validate_song(raw_song)
            inserted = insert_song(song)

            if inserted:
                inserted_count += 1
            else:
                skipped_count += 1

        except Exception as error:
            error_count += 1
            print(f"Error processing song {raw_song}: {error}")

    print("\nLoad complete.")
    print(f"Inserted: {inserted_count}")
    print(f"Skipped duplicates: {skipped_count}")
    print(f"Errors: {error_count}")


if __name__ == "__main__":
    main()