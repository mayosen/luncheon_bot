from datetime import datetime
import peewee as pw

from config import POSTGRES_USER, POSTGRES_PASSWORD

db = pw.PostgresqlDatabase("lunch", user=POSTGRES_USER, password=POSTGRES_PASSWORD)


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
    joined = pw.DateTimeField(default=datetime.now)

    def __str__(self):
        return f"@{self.username}" if self.username else f"<code>{self.id}</code>"


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

    def __str__(self):
        return f"Order #{self.id} of User: {str(self.user)}"


class Product(BaseModel):
    id = pw.AutoField()
    category = pw.CharField()
    title = pw.CharField()
    price = pw.IntegerField()
    photo = pw.CharField()

    def __str__(self):
        return f"{self.title}, {self.price} р."


class OrderItem(BaseModel):
    id = pw.AutoField()
    order = pw.ForeignKeyField(Order, backref="items", on_delete="CASCADE")
    product = pw.ForeignKeyField(Product, on_delete="CASCADE")


if __name__ == "__main__":
    db.create_tables([User, Order, Product, OrderItem])
