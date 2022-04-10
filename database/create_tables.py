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
    status = pw.CharField(default="В обработке")
    user = pw.ForeignKeyField(User, backref="orders", on_delete="CASCADE")
    address = pw.CharField()
    phone = pw.CharField()
    products = pw.CharField()
    rate = pw.IntegerField(default=0)
    feedback = pw.TextField()
    feedback_attachments = pw.TextField()


class Product(BaseModel):
    id = pw.AutoField()
    category = pw.CharField()
    title = pw.CharField()
    price = pw.IntegerField()
    photo = pw.CharField()          # Telegram photo file_id


db.create_tables([User, Order, Product])
