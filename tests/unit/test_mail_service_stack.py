import aws_cdk as core
import aws_cdk.assertions as assertions

from mail_service.mail_service_stack import MailServiceStack

# example tests. To run these tests, uncomment this file along with the example
# resource in mail_service/mail_service_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = MailServiceStack(app, "mail-service")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
