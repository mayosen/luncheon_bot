from os import environ


class DatabaseUrl:
    def __init__(self, url: str):
        url = url.removeprefix("postgres://")
        sep = url.find(":")
        self.user = url[:sep]
        url = url[sep + 1:]
        sep = url.find("@")
        self.password = url[:sep]
        url = url[sep + 1:]
        sep = url.find(":")
        self.host = url[:sep]
        url = url[sep + 1:]
        sep = url.find("/")
        self.port = url[:sep]
        self.database = url[sep + 1:]


TOKEN = environ.get("BOT_TOKEN")
ADMIN_PASSWORD = environ.get("ADMIN_PASSWORD")
POSTGRES = DatabaseUrl(environ.get("DATABASE_URL"))
