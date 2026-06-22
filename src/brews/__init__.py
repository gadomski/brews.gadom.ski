import uvicorn


def main() -> None:
    """Run the Brews web server."""
    uvicorn.run("brews.app:app", host="127.0.0.1", port=8000)
