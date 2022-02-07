from aws_cdk import (
     Duration,
    Stack,
     aws_sqs as sqs,
)
from constructs import Construct
from . import mail_service


class MailServiceStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        mail_service.MailService(self, "message")
        # The code that defines your stack goes here

        # example resource
        #queue = sqs.Queue(
        #     self, "MailServiceQueue",
        #     visibility_timeout=Duration.seconds(300),
        #)

