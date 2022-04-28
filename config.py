from os import environ


class DatabaseUrl:
    __slots__ = ("user", "password", "host", "port", "database")

    def __init__(self, url: str = None):
        if not url:
            self.user = None
            self.password = None
            self.host = None
            self.port = None
            self.database = None
            return

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

    def create_url(self):
        return (
                "postgres://" + self.user + ":" + self.password +
                "@" + self.host + ":" + self.port + "/" + self.database
        )


TOKEN = environ.get("BOT_TOKEN")
ADMIN_PASSWORD = environ.get("ADMIN_PASSWORD")
POSTGRES = DatabaseUrl(environ.get("DATABASE_URL"))
