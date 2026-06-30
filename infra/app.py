from aws_cdk import App, Environment
from brews_infra import BrewsStack

app = App()
BrewsStack(
    app,
    "BrewsStack",
    env=Environment(account="533267395928", region="us-west-2"),
)
app.synth()
