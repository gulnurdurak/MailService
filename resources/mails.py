import boto3
from botocore.exceptions import ClientError
import requests

ses = boto3.client("ses")

# Get the service resource.
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('users')


def subscribe_user(first_name, last_name, mail_address):
    table.put_item(
        Item=dict(mail_address=mail_address, first_name=first_name, last_name=last_name)
    )
    send_verification_email(mail_address)


def send_verification_email(mail_address):
    response = ses.verify_email_identity(
        EmailAddress=mail_address
    )


def check_user_verification_status(mail_address):
    response = ses.get_identity_verification_attributes(
        Identities=[
            mail_address,
        ],
    )
    status = response['VerificationAttributes'][mail_address]['VerificationStatus']
    return status


def update_user_item(mail_address):
    table.update_item(
        Key={
            'mail_address': mail_address,
        },
        UpdateExpression='SET verified = :val1',
        ExpressionAttributeValues={
            ':val1': True
        }
    )


def get_user_info(mail_address):
    response = table.get_item(
        Key={
            'mail_address': mail_address,
        }
    )


def unsubscribe_user(mail_address):
    table.delete_item(
        Key={
            'mail_address': mail_address
        }
    )


def get_bitcoin_info():
    response = requests.get("https://api.coindesk.com/v1/bpi/currentprice.json")
    data = response.json()
    return {data["bpi"]["USD"]["code"]: data["bpi"]["USD"]["rate"]}


def send_mail_function(subject, text):
    to_address = list_subscribers_mails()
    print(to_address)
    try:
        response = ses.send_email(
            Destination={
                "ToAddresses": to_address,
            },
            Message={
                "Body": {
                    "Html": {
                        "Charset": "UTF-8",
                        "Data": text,
                    },
                    "Text": {
                        "Charset": "UTF-8",
                        "Data": "This is for those who cannot read HTML.",
                    },
                },
                "Subject": {
                    "Charset": "UTF-8",
                    "Data": subject,
                },
            },
            Source=" gulnurdurak20@gmail.com",
        )
    except ClientError as e:
        return e.response["Error"]["Message"]
    else:
        return "Email sent!"


def create_dynamodb_table():
    # Create the DynamoDB table.
    table = dynamodb.create_table(
        TableName='users',
        KeySchema=[
            {
                'AttributeName': 'mail_address',
                'KeyType': 'HASH'
            },
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'mail_address',
                'AttributeType': 'S'
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )

    # Wait until the table exists.
    table.wait_until_exists()

    # Print out some data about the table.
    print(table.item_count)


def list_subscribers_mails():
    to_address = [i['mail_address'] for i in table.scan()['Items']]
    return to_address


if __name__ == "__main__":
   print('test')
