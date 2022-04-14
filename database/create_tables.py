"""
Вынесено в отдельный модуль, чтобы хранить файл с БД в /database
"""


import peewee as pw


db = pw.SqliteDatabase("database.sqlite3")


class BaseModel(pw.Model):
    class Meta:
        database = db


class User(BaseModel):
    id = pw.IntegerField(primary_key=True)
    status = pw.CharField()
    name = pw.CharField()
    username = pw.CharField()
    address = pw.CharField(default="")
    phone = pw.CharField(default="")


class Order(BaseModel):
    id = pw.AutoField()
    status = pw.CharField()
    user = pw.ForeignKeyField(User, backref="orders", on_delete="CASCADE")
    address = pw.CharField()
    phone = pw.CharField()
    created = pw.DateTimeField()
    rate = pw.IntegerField(default=0)
    feedback = pw.TextField(default="")
    attachments = pw.TextField(default="")


class Product(BaseModel):
    id = pw.AutoField()
    category = pw.CharField()
    title = pw.CharField()
    price = pw.IntegerField()
    photo = pw.CharField()


class OrderItem(BaseModel):
    id = pw.AutoField()
    order = pw.ForeignKeyField(Order, backref="items", on_delete="CASCADE")
    product = pw.ForeignKeyField(Product, on_delete="CASCADE")


db.create_tables([User, Order, Product, OrderItem])
