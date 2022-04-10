import peewee as pw

from .models import User, Order, Product


if __name__ == "__main__":
    db = pw.SqliteDatabase("database.sqlite3")
    db.create_tables([User, Order, Product])
