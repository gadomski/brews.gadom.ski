from pathlib import Path

from aws_cdk import BundlingOptions, CfnOutput, Duration, Stack
from aws_cdk.aws_apigatewayv2 import HttpApi
from aws_cdk.aws_apigatewayv2_integrations import HttpLambdaIntegration
from aws_cdk.aws_dynamodb import Attribute, AttributeType, Billing, TableV2
from aws_cdk.aws_iam import PolicyStatement
from aws_cdk.aws_lambda import Architecture, Code, Function, Runtime
from aws_cdk.aws_s3 import Bucket, CorsRule, HttpMethods

_PROJECT_ROOT = Path(__file__).resolve().parents[3]


class BrewsStack(Stack):
    def __init__(self, scope, id, **kwargs):
        super().__init__(scope, id, **kwargs)

        table = TableV2(
            self,
            "table",
            partition_key=Attribute(name="pk", type=AttributeType.STRING),
            billing=Billing.on_demand(),
        )

        bucket = Bucket(
            self,
            "bucket",
            cors=[
                CorsRule(
                    allowed_methods=[HttpMethods.PUT],
                    allowed_origins=[
                        "https://brews.gadom.ski",
                        "http://localhost:5173",
                    ],
                    allowed_headers=["*"],
                    max_age=3000,
                )
            ],
        )

        function = Function(
            self,
            "api",
            runtime=Runtime.PYTHON_3_13,
            architecture=Architecture.ARM_64,
            handler="brews.handler.handler",
            timeout=Duration.seconds(30),
            memory_size=512,
            environment={
                "BREWS_TABLE_NAME": table.table_name,
                "BREWS_IMAGE_BUCKET_NAME": bucket.bucket_name,
                "ANTHROPIC_API_KEY_PARAM": "/brews/anthropic-api-key",
                "UPLOAD_TOKEN_PARAM": "/brews/upload-token",
            },
            code=Code.from_asset(
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
                    image=Runtime.PYTHON_3_13.bundling_image,
                    platform="linux/arm64",
                    command=[
                        "bash",
                        "-c",
                        "pip install '.[lambda]' --target /asset-output",
                    ],
                ),
            ),
        )

        table.grant_read_write_data(function)
        bucket.grant_read_write(function)

        function.add_to_role_policy(
            PolicyStatement(
                actions=["ssm:GetParameter"],
                resources=[
                    self.format_arn(
                        service="ssm", resource="parameter", resource_name="brews/*"
                    )
                ],
            )
        )
        function.add_to_role_policy(
            PolicyStatement(
                actions=["kms:Decrypt"],
                resources=["*"],
                conditions={
                    "StringEquals": {
                        "kms:ViaService": f"ssm.{self.region}.amazonaws.com"
                    }
                },
            )
        )

        http_api = HttpApi(
            self,
            "HttpApi",
            default_integration=HttpLambdaIntegration("ApiIntegration", function),  # pyright: ignore[reportArgumentType]
        )

        CfnOutput(self, "ApiUrl", value=http_api.url or "")
