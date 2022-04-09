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
    status = pw.CharField(default="В обработке")
    user = pw.ForeignKeyField(User, backref="orders", on_delete="CASCADE")
    address = pw.CharField()
    phone = pw.CharField()
    products = pw.CharField()
    rate = pw.IntegerField()
    feedback = pw.TextField()
    feedback_attachments = pw.TextField()


class Product(BaseModel):
    id = pw.AutoField()
    category = pw.CharField()
    title = pw.CharField()
    price = pw.IntegerField()


if __name__ == "__main__":
    # Приходится менять название на "database.sqlite3"
    db.create_tables([User, Order, Product])
