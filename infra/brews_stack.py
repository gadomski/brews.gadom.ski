from pathlib import Path

from aws_cdk import BundlingOptions, CfnOutput, Duration, Stack
from aws_cdk import aws_apigatewayv2 as apigwv2
from aws_cdk import aws_apigatewayv2_integrations as integrations
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_s3 as s3
from constructs import Construct

_PROJECT_ROOT = Path(__file__).resolve().parent.parent


class BrewsStack(Stack):
    """Backend infrastructure: DynamoDB, the FastAPI Lambda, and the HTTP API."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        table = dynamodb.TableV2(
            self,
            "BeerTable",
            partition_key=dynamodb.Attribute(
                name="pk", type=dynamodb.AttributeType.STRING
            ),
            billing=dynamodb.Billing.on_demand(),
        )

        bucket = s3.Bucket(
            self,
            "ImageBucket",
            cors=[
                s3.CorsRule(
                    allowed_methods=[s3.HttpMethods.PUT],
                    allowed_origins=[
                        "https://brews.gadom.ski",
                        "http://localhost:5173",
                    ],
                    allowed_headers=["*"],
                    max_age=3000,
                )
            ],
        )

        function = lambda_.Function(
            self,
            "ApiFunction",
            runtime=lambda_.Runtime.PYTHON_3_13,
            architecture=lambda_.Architecture.ARM_64,
            handler="brews.app.handler",
            timeout=Duration.seconds(30),
            memory_size=512,
            environment={
                "BREWS_TABLE_NAME": table.table_name,
                "BREWS_BUCKET_NAME": bucket.bucket_name,
                "ANTHROPIC_API_KEY_PARAM": "/brews/anthropic-api-key",
                "UPLOAD_TOKEN_PARAM": "/brews/upload-token",
            },
            code=lambda_.Code.from_asset(
                str(_PROJECT_ROOT),
                exclude=[
                    ".venv",
                    "frontend",
                    "infra",
                    "docs",
                    "node_modules",
                    ".git",
                    "tests",
                    ".superpowers",
                    "**/__pycache__",
                ],
                bundling=BundlingOptions(
                    image=lambda_.Runtime.PYTHON_3_13.bundling_image,
                    platform="linux/arm64",
                    command=["bash", "-c", "pip install . --target /asset-output"],
                ),
            ),
        )

        table.grant_read_write_data(function)
        bucket.grant_read_write(function)

        function.add_to_role_policy(
            iam.PolicyStatement(
                actions=["ssm:GetParameter"],
                resources=[
                    self.format_arn(
                        service="ssm", resource="parameter", resource_name="brews/*"
                    )
                ],
            )
        )
        function.add_to_role_policy(
            iam.PolicyStatement(
                actions=["kms:Decrypt"],
                resources=["*"],
                conditions={
                    "StringEquals": {
                        "kms:ViaService": f"ssm.{self.region}.amazonaws.com"
                    }
                },
            )
        )

        http_api = apigwv2.HttpApi(
            self,
            "HttpApi",
            default_integration=integrations.HttpLambdaIntegration(
                "ApiIntegration", function
            ),
        )

        CfnOutput(self, "ApiUrl", value=http_api.url or "")
