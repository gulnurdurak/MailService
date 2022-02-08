import json
import mails


def send_mail_handler(event, context):
    body = json.loads(event["body"])
    endpoint_name = event["requestContext"]["resourcePath"]
    if endpoint_name == '/MailService/sendMail':
        response_message = mails.send_mail_function(subject=body["subject"], text=body["text"])
    else:
        response_message = ""
    return generate_response(response_message)


def user_handler(event, context):

    endpoint_name = event["requestContext"]["resourcePath"]

    if endpoint_name == '/MailService/subscribeUser':
        body = json.loads(event["body"])
        mails.subscribe_user(mail_address=body["mail_address"], first_name=body["first_name"],
                             last_name=body["last_name"])
        response_message = "User successfully subscribed."
    elif endpoint_name == '/MailService/unsubscribeUser':
        body = json.loads(event["body"])
        mails.unsubscribe_user(mail_address=body["mail_address"])
        response_message = "User successfully unsubscribed."

    elif endpoint_name == '/MailService/listSubscribers':
        mail_addresses = mails.list_subscribers_mails()
        response_message = mail_addresses

    else:
        response_message = "Error! Check the endpoint. "+ endpoint_name

    return generate_response(response_message)


def generate_response(response_message):
    response = {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
        },
        "body": json.dumps(
            {
                "success": True,
                "content": response_message,
            }
        ),
    }
    return response


if __name__ == "__main__":
    # xx = my_handler({}, {})
    print()
