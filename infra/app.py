import aws_cdk as cdk
from brews_stack import BrewsStack

app = cdk.App()
BrewsStack(app, "BrewsStack")
app.synth()
