import peewee as pw


db = pw.SqliteDatabase("database/database.sqlite3")


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

    def __str__(self):
        info = (f"{self.status}: {self.name}\n"
                f"id: {self.id}\n"
                f"username: {self.username}\n"
                f"address: {self.address}\n"
                f"phone: {self.phone}\n")
        return info


class Order(BaseModel):
    id = pw.AutoField()
    status = pw.CharField()
    user = pw.ForeignKeyField(User, backref="orders", on_delete="CASCADE")
    address = pw.CharField()
    phone = pw.CharField()
    rate = pw.IntegerField(default=0)
    feedback = pw.TextField()
    feedback_attachments = pw.TextField()


class Product(BaseModel):
    id = pw.AutoField()
    category = pw.CharField()
    title = pw.CharField()
    price = pw.IntegerField()
    photo = pw.CharField()


class OrderItem(BaseModel):
    id = pw.AutoField()
    order_id = pw.ForeignKeyField(Order, backref="items", on_delete="CASCADE")
    product_item = pw.ForeignKeyField(Product, on_delete="CASCADE")
