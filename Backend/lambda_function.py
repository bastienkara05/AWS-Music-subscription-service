import json
import boto3
from boto3.dynamodb.conditions import Key, Attr

REGION = "us-east-1"

dynamodb = boto3.resource("dynamodb", region_name=REGION)

login_table = dynamodb.Table("login")
music_table = dynamodb.Table("music")
subscriptions_table = dynamodb.Table("subscriptions")


def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,POST,DELETE,OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        },
        "body": json.dumps(body)
    }


def build_artist_title_year(artist, title, year):
    return f"{artist}#{title}#{year}"


def get_body(event):
    if not event.get("body"):
        return {}
    return json.loads(event["body"])


def get_method_and_path(event):
    method = event.get("requestContext", {}).get("http", {}).get("method")
    path = event.get("rawPath", "")

    if not method:
        method = event.get("httpMethod", "GET")

    return method, path


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


def query_music(params):
    title = params.get("title")
    artist = params.get("artist")
    year = params.get("year")
    album = params.get("album")

    if not any([title, artist, year, album]):
        return response(400, {
            "success": False,
            "message": "At least one field must be completed"
        })

    items = []

    if artist and year:
        result = music_table.query(
            IndexName="LSI_Year",
            KeyConditionExpression=Key("artist").eq(artist) & Key("year").eq(year)
        )
        items = result.get("Items", [])

    elif artist:
        result = music_table.query(
            KeyConditionExpression=Key("artist").eq(artist)
        )
        items = result.get("Items", [])

    elif title:
        result = music_table.query(
            IndexName="GSI_Title",
            KeyConditionExpression=Key("title").eq(title)
        )
        items = result.get("Items", [])

    else:
        filter_expr = None

        if year:
            filter_expr = Attr("year").eq(year)

        if album:
            condition = Attr("album").eq(album)
            filter_expr = condition if filter_expr is None else filter_expr & condition

        if filter_expr:
            result = music_table.scan(FilterExpression=filter_expr)
        else:
            result = music_table.scan()

        items = result.get("Items", [])

    items = apply_filters(items, title, artist, year, album)

    if not items:
        return response(200, {
            "success": False,
            "message": "No result is retrieved. Please query again",
            "items": []
        })

    return response(200, {
        "success": True,
        "message": "query successful",
        "items": items
    })


def register_user(body):
    email = body.get("email", "").strip()
    username = body.get("username", "").strip()
    password = body.get("password", "").strip()

    if not email or not username or not password:
        return response(400, {
            "success": False,
            "message": "email, username and password are required"
        })

    existing = login_table.get_item(Key={"email": email}).get("Item")

    if existing:
        return response(200, {
            "success": False,
            "message": "The email already exists"
        })

    login_table.put_item(
        Item={
            "email": email,
            "user_name": username,
            "password": password
        }
    )

    return response(200, {
        "success": True,
        "message": "registration successful"
    })


def login_user(body):
    email = body.get("email", "").strip()
    password = body.get("password", "").strip()

    user = login_table.get_item(Key={"email": email}).get("Item")

    if not user or user.get("password") != password:
        return response(200, {
            "success": False,
            "message": "email or password is invalid"
        })

    return response(200, {
        "success": True,
        "message": "login successful",
        "user": {
            "email": user["email"],
            "user_name": user.get("user_name")
        }
    })


def get_subscriptions(params):
    email = params.get("email", "").strip()

    if not email:
        return response(400, {
            "success": False,
            "message": "email is required"
        })

    result = subscriptions_table.query(
        KeyConditionExpression=Key("email").eq(email)
    )

    return response(200, {
        "success": True,
        "items": result.get("Items", [])
    })


def add_subscription(body):
    email = body.get("email", "").strip()
    song = body.get("song", {})

    artist = song.get("artist", "").strip()
    title = song.get("title", "").strip()
    year = str(song.get("year", "")).strip()
    album = song.get("album", "").strip()

    if not email or not artist or not title or not year:
        return response(400, {
            "success": False,
            "message": "email and song details are required"
        })

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

    return response(200, {
        "success": True,
        "message": "subscription added",
        "item": item
    })


def delete_subscription(params):
    email = params.get("email", "").strip()
    artist_title_year = params.get("artist_title_year", "").strip()

    if not email or not artist_title_year:
        return response(400, {
            "success": False,
            "message": "email and artist_title_year are required"
        })

    subscriptions_table.delete_item(
        Key={
            "email": email,
            "artist_title_year": artist_title_year
        }
    )

    return response(200, {
        "success": True,
        "message": "subscription removed"
    })


def lambda_handler(event, context):
    method, path = get_method_and_path(event)
    params = event.get("queryStringParameters") or {}

    if method == "OPTIONS":
        return response(200, {"message": "CORS preflight successful"})

    if method == "GET" and path.endswith("/music-query-lambda"):
        return query_music(params)

    if method == "GET" and path.endswith("/subscriptions"):
        return get_subscriptions(params)

    if method == "POST" and path.endswith("/register"):
        return register_user(get_body(event))

    if method == "POST" and path.endswith("/login"):
        return login_user(get_body(event))

    if method == "POST" and path.endswith("/subscriptions"):
        return add_subscription(get_body(event))

    if method == "DELETE" and path.endswith("/subscriptions"):
        return delete_subscription(params)

    return response(404, {
        "success": False,
        "message": f"No route for {method} {path}"
    })