# Brews backend infrastructure (AWS CDK)

Provisions DynamoDB, the FastAPI Lambda (packaged with Docker bundling), and an
HTTP API Gateway.

## Prerequisites

- AWS credentials configured locally (`aws configure` / SSO).
- Docker running (Lambda bundling builds the dependencies in a container).
- The CDK CLI: `npm install -g aws-cdk` (or use `npx cdk`).
- `uv sync` in this directory.

## One-time secret setup

Create the two SecureString parameters the Lambda reads:

```bash
aws ssm put-parameter --name /brews/anthropic-api-key --type SecureString --value "sk-..."
aws ssm put-parameter --name /brews/upload-token --type SecureString --value "your-upload-token"
```

## Deploy

```bash
cd infra
uv run cdk bootstrap   # once per account/region
uv run cdk deploy
```

Note the `ApiUrl` output. Then:

1. Set the GitHub repo variable `VITE_API_BASE_URL` to that URL.
2. Enable GitHub Pages with source "GitHub Actions".
3. Add a DNS record in Gandi for `brews.gadom.ski` pointing at GitHub Pages.
