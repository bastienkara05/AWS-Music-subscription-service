import boto3
from botocore.exceptions import ClientError

REGION = "us-east-1"

LOGIN_TABLE = "login"
MUSIC_TABLE = "music"
SUBSCRIPTIONS_TABLE = "subscriptions"

dynamodb = boto3.client("dynamodb", region_name=REGION)


def table_exists(table_name):
    try:
        dynamodb.describe_table(TableName=table_name)
        return True
    except ClientError as error:
        if error.response["Error"]["Code"] == "ResourceNotFoundException":
            return False
        raise


def create_login_table():
    if table_exists(LOGIN_TABLE):
        print(f"Table '{LOGIN_TABLE}' already exists.")
        return

    dynamodb.create_table(
        TableName=LOGIN_TABLE,
        AttributeDefinitions=[
            {"AttributeName": "email", "AttributeType": "S"},
        ],
        KeySchema=[
            {"AttributeName": "email", "KeyType": "HASH"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )

    dynamodb.get_waiter("table_exists").wait(TableName=LOGIN_TABLE)
    print(f"Table '{LOGIN_TABLE}' created successfully.")


def create_music_table():
    if table_exists(MUSIC_TABLE):
        print(f"Table '{MUSIC_TABLE}' already exists.")
        return

    dynamodb.create_table(
        TableName=MUSIC_TABLE,
        AttributeDefinitions=[
            {"AttributeName": "artist", "AttributeType": "S"},
            {"AttributeName": "title_year", "AttributeType": "S"},
            {"AttributeName": "year", "AttributeType": "S"},
            {"AttributeName": "title", "AttributeType": "S"},
        ],
        KeySchema=[
            {"AttributeName": "artist", "KeyType": "HASH"},
            {"AttributeName": "title_year", "KeyType": "RANGE"},
        ],
        LocalSecondaryIndexes=[
            {
                "IndexName": "LSI_Year",
                "KeySchema": [
                    {"AttributeName": "artist", "KeyType": "HASH"},
                    {"AttributeName": "year", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],
        GlobalSecondaryIndexes=[
            {
                "IndexName": "GSI_Title",
                "KeySchema": [
                    {"AttributeName": "title", "KeyType": "HASH"},
                    {"AttributeName": "artist", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],
        BillingMode="PAY_PER_REQUEST",
    )

    dynamodb.get_waiter("table_exists").wait(TableName=MUSIC_TABLE)
    print(f"Table '{MUSIC_TABLE}' created successfully.")


def create_subscriptions_table():
    if table_exists(SUBSCRIPTIONS_TABLE):
        print(f"Table '{SUBSCRIPTIONS_TABLE}' already exists.")
        return

    dynamodb.create_table(
        TableName=SUBSCRIPTIONS_TABLE,
        AttributeDefinitions=[
            {"AttributeName": "email", "AttributeType": "S"},
            {"AttributeName": "artist_title_year", "AttributeType": "S"},
        ],
        KeySchema=[
            {"AttributeName": "email", "KeyType": "HASH"},
            {"AttributeName": "artist_title_year", "KeyType": "RANGE"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )

    dynamodb.get_waiter("table_exists").wait(TableName=SUBSCRIPTIONS_TABLE)
    print(f"Table '{SUBSCRIPTIONS_TABLE}' created successfully.")


def main():
    create_login_table()
    create_music_table()
    create_subscriptions_table()
    print("All required tables are ready.")


if __name__ == "__main__":
    main()