import boto3

REGION = "us-east-1"
LOGIN_TABLE = "login"


# Generic placeholders for seeding demo users.
USER_ID = "demouser"
NAME = "DemoUser"
EMAIL_DOMAIN = "example.com"

dynamodb = boto3.resource("dynamodb", region_name=REGION)
table = dynamodb.Table(LOGIN_TABLE)


def generate_users():
    users = []

    base_email = f"{USER_ID}@{EMAIL_DOMAIN}"

    for i in range(10):
        # email
        if i == 0:
            email = base_email
        else:
            email = f"{USER_ID}+{i}@{EMAIL_DOMAIN}"

        # username
        username = f"{NAME}{i}"

        # password pattern
        password = "".join(str((i + j) % 10) for j in range(6))

        users.append({
            "email": email,
            "user_name": username,
            "password": password
        })

    return users


def seed_users():
    users = generate_users()

    for user in users:
        table.put_item(Item=user)
        print(f"Seeded: {user['email']} | {user['user_name']} | {user['password']}")


if __name__ == "__main__":
    seed_users()