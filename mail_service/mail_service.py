import os
import subprocess

from constructs import Construct
from aws_cdk import (aws_lambda as lambda_,
                     aws_iam as iam)
from aws_cdk.aws_apigateway import (
    RestApi,
    LambdaIntegration
)


class MailService(Construct):

    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        lambda_dependency_layer = self.create_dependencies_layer("MailServiceStackLayer")
        execution_role = self.create_role('MailServiceRole', 'lambda')

        def create_lambda_function(handler_path, id):
            my_lambda_function = lambda_.Function(self, id,
                                                  runtime=lambda_.Runtime.PYTHON_3_6,
                                                  code=lambda_.Code.from_asset("resources"),
                                                  role=execution_role,
                                                  handler=handler_path,
                                                  layers=[lambda_dependency_layer],
                                                  )

            return my_lambda_function

        # api gateway core
        api_gateway = RestApi(self, 'ICS_API_GATEWAY', rest_api_name='MailServiceApiGateway')
        #  root
        api_gateway_resource = api_gateway.root.add_resource("MailService")
        # to send mail
        api_gateway_send_mail_resource = api_gateway_resource.add_resource('sendMail')
        # to add a user to the mail list
        api_gateway_subscribe_user_resource = api_gateway_resource.add_resource('subscribeUser')
        # to delete a user to the mail list
        api_gateway_unsubscribe_user_resource = api_gateway_resource.add_resource('unsubscribeUser')
        # to list all subscriber mail addresses
        api_gateway_list_subscribers_resource = api_gateway_resource.add_resource('listSubscribers')
        # to change sending mail frequency
        api_gateway_change_frequency_resource = api_gateway_resource.add_resource('changeFrequency')

        # lambda integration
        integration_user = LambdaIntegration(create_lambda_function('lambda_function'
                                                                    '.user_handler', "userMailService"))

        integration_send_mail = LambdaIntegration(create_lambda_function('lambda_function'
                                                                         '.send_mail_handler', "MailService"))

        # adding methods
        api_gateway_send_mail_resource.add_method('POST', integration_send_mail)
        api_gateway_subscribe_user_resource.add_method('POST', integration_user)
        api_gateway_unsubscribe_user_resource.add_method('POST', integration_user)
        api_gateway_list_subscribers_resource.add_method('GET', integration_user)
        # api_gateway_change_frequency_resource.add_method('POST')

    def create_dependencies_layer(self, project_name) -> lambda_.LayerVersion:
        requirements_file = f'requirements.txt'
        output_dir = f'../.build/deps'

        if not os.environ.get('SKIP_PIP'):
            subprocess.check_call(
                f'pip install -r {requirements_file} -t {output_dir}/python'.split()
            )

        layer_id = f'{project_name}-dependencies'
        layer_code = lambda_.Code.from_asset(output_dir)

        return lambda_.LayerVersion(self, layer_id, code=layer_code)

    def create_role(self, role_name, role_consumer):
        policy_statement = iam.PolicyStatement(actions=[
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents",
            "ses:SendEmail",
            "ses:VerifyEmailIdentity",
            "dynamodb:BatchGetItem",
            "dynamodb:GetItem",
            "dynamodb:Query",
            "dynamodb:Scan",
            "dynamodb:BatchWriteItem",
            "dynamodb:PutItem",
            "dynamodb:UpdateItem",
            "dynamodb:DeleteItem",
        ], resources=["*"])
        policy_document = iam.PolicyDocument(statements=[policy_statement])
        role = iam.Role(
            scope=self,
            id=f'{role_name}{role_consumer}',
            role_name=f'{role_name}{role_consumer}',
            inline_policies=[policy_document],
            assumed_by=iam.ServicePrincipal(f'{role_consumer}.amazonaws.com'),
        )
        return role
