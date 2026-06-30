import brews.app

app = brews.app.create()


def main() -> None:
    import uvicorn

    uvicorn.run("brews.cli:app", host="127.0.0.1", port=8000, reload=True)
