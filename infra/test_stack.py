import aws_cdk as cdk
from aws_cdk.assertions import Match, Template
from brews_stack import BrewsStack


def _template():
    app = cdk.App(context={"aws:cdk:bundling-stacks": []})
    return Template.from_stack(BrewsStack(app, "TestStack"))


def test_has_table_lambda_and_api():
    template = _template()
    template.resource_count_is("AWS::DynamoDB::GlobalTable", 1)
    template.resource_count_is("AWS::Lambda::Function", 1)
    template.resource_count_is("AWS::ApiGatewayV2::Api", 1)


def test_lambda_handler_is_wired():
    _template().has_resource_properties(
        "AWS::Lambda::Function", {"Handler": "brews.app.handler"}
    )


def test_lambda_env_vars():
    _template().has_resource_properties(
        "AWS::Lambda::Function",
        {
            "Environment": {
                "Variables": Match.object_like(
                    {
                        "ANTHROPIC_API_KEY_PARAM": "/brews/anthropic-api-key",
                        "UPLOAD_TOKEN_PARAM": "/brews/upload-token",
                        "BREWS_TABLE_NAME": Match.any_value(),
                    }
                )
            }
        },
    )


def test_lambda_architecture_is_arm64():
    _template().has_resource_properties(
        "AWS::Lambda::Function", {"Architectures": ["arm64"]}
    )


def test_has_image_bucket():
    _template().resource_count_is("AWS::S3::Bucket", 1)


def test_lambda_has_bucket_env_var():
    _template().has_resource_properties(
        "AWS::Lambda::Function",
        {
            "Environment": {
                "Variables": Match.object_like(
                    {"BREWS_BUCKET_NAME": Match.any_value()}
                )
            }
        },
    )


def test_bucket_allows_put_cors():
    _template().has_resource_properties(
        "AWS::S3::Bucket",
        {
            "CorsConfiguration": {
                "CorsRules": Match.array_with(
                    [
                        Match.object_like(
                            {
                                "AllowedMethods": ["PUT"],
                                "AllowedOrigins": [
                                    "https://brews.gadom.ski",
                                    "http://localhost:5173",
                                ],
                            }
                        )
                    ]
                )
            }
        },
    )
