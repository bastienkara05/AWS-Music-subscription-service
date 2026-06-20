import re
import boto3
from boto3.dynamodb.conditions import Key, Attr

REGION = "us-east-1"
BUCKET_NAME = "118group-music-images"

dynamodb = boto3.resource("dynamodb", region_name=REGION)

login_table = dynamodb.Table("login")
music_table = dynamodb.Table("music")
subscriptions_table = dynamodb.Table("subscriptions")


def build_s3_image_url(artist):
    filename = artist.strip().lower()
    filename = re.sub(r"[^a-z0-9]+", "_", filename).strip("_")
    return f"https://{BUCKET_NAME}.s3.amazonaws.com/artist-images/{filename}.jpg"


def build_artist_title_year(artist, title, year):
    return f"{artist}#{title}#{year}"


def add_image_urls(items):
    for item in items:
        if "artist" in item:
            item["s3_image_url"] = build_s3_image_url(item["artist"])
    return items


def apply_filters(items, title=None, artist=None, year=None, album=None):
    if title:
        items = [item for item in items if item.get("title") == title]

    if artist:
        items = [item for item in items if item.get("artist") == artist]

    if year:
        items = [item for item in items if item.get("year") == year]

    if album:
        items = [item for item in items if item.get("album") == album]

    return items


def login_user(email, password):
    email = email.strip()
    password = password.strip()

    user = login_table.get_item(Key={"email": email}).get("Item")

    if not user or user.get("password") != password:
        return {"success": False, "message": "email or password is invalid"}

    return {
        "success": True,
        "message": "login successful",
        "user": {
            "email": user["email"],
            "user_name": user.get("user_name")
        }
    }


def register_user(email, username, password):
    email = email.strip()
    username = username.strip()
    password = password.strip()

    existing = login_table.get_item(Key={"email": email}).get("Item")

    if existing:
        return {"success": False, "message": "The email already exists"}

    login_table.put_item(
        Item={
            "email": email,
            "user_name": username,
            "password": password
        }
    )

    return {"success": True, "message": "registration successful"}


def query_music(title=None, artist=None, year=None, album=None):
    title = title.strip() if title else None
    artist = artist.strip() if artist else None
    year = year.strip() if year else None
    album = album.strip() if album else None

    if not any([title, artist, year, album]):
        return {
            "success": False,
            "message": "At least one field must be completed",
            "items": []
        }

    try:
        items = []

        if artist and year:
            response = music_table.query(
                IndexName="LSI_Year",
                KeyConditionExpression=Key("artist").eq(artist) & Key("year").eq(year)
            )
            items = response.get("Items", [])

        elif artist:
            response = music_table.query(
                KeyConditionExpression=Key("artist").eq(artist)
            )
            items = response.get("Items", [])

        elif title:
            response = music_table.query(
                IndexName="GSI_Title",
                KeyConditionExpression=Key("title").eq(title)
            )
            items = response.get("Items", [])

        else:
            filter_expr = None

            if year:
                filter_expr = Attr("year").eq(year)

            if album:
                condition = Attr("album").eq(album)
                filter_expr = condition if filter_expr is None else filter_expr & condition

            if filter_expr is not None:
                response = music_table.scan(FilterExpression=filter_expr)
            else:
                response = music_table.scan()

            items.extend(response.get("Items", []))

            while "LastEvaluatedKey" in response:
                scan_args = {
                    "ExclusiveStartKey": response["LastEvaluatedKey"]
                }

                if filter_expr is not None:
                    scan_args["FilterExpression"] = filter_expr

                response = music_table.scan(**scan_args)
                items.extend(response.get("Items", []))

        items = apply_filters(
            items,
            title=title,
            artist=artist,
            year=year,
            album=album
        )

        if not items:
            return {
                "success": False,
                "message": "No result is retrieved. Please query again",
                "items": []
            }

        items = add_image_urls(items)

        return {
            "success": True,
            "message": "query successful",
            "items": items
        }

    except Exception as error:
        return {
            "success": False,
            "message": f"query error: {str(error)}",
            "items": []
        }


def get_subscriptions(email):
    email = email.strip()

    response = subscriptions_table.query(
        KeyConditionExpression=Key("email").eq(email)
    )

    items = response.get("Items", [])
    items = add_image_urls(items)

    return {
        "success": True,
        "items": items
    }


def add_subscription(email, song):
    email = email.strip()

    artist = song["artist"].strip()
    title = song["title"].strip()
    year = str(song["year"]).strip()
    album = song["album"].strip()

    artist_title_year = build_artist_title_year(artist, title, year)

    item = {
        "email": email,
        "artist_title_year": artist_title_year,
        "artist": artist,
        "title": title,
        "year": year,
        "album": album
    }

    subscriptions_table.put_item(Item=item)

    return {
        "success": True,
        "message": "subscription added",
        "item": item
    }


def remove_subscription(email, artist_title_year):
    email = email.strip()

    subscriptions_table.delete_item(
        Key={
            "email": email,
            "artist_title_year": artist_title_year
        }
    )

    return {
        "success": True,
        "message": "subscription removed"
    }