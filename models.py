from peewee import Model, SqliteDatabase, CharField, ForeignKeyField, IntegerField, DecimalField, TextField, fn

data = SqliteDatabase("betsy_boop.db")


class BaseModel(Model):
    class Meta:
        database = data


class User(BaseModel):
    name = CharField(max_length=50)


class Address(BaseModel):
    street = CharField(max_length=50)
    number = IntegerField()
    number_addition = CharField(max_length=5)
    zip_code = CharField(max_length=6)
    city = CharField(max_length=50)
    country = CharField(max_length=50)


class UserAddresses(BaseModel):
    user_id = ForeignKeyField(User)
    home_address_id = ForeignKeyField(Address)
    billing_address_id = ForeignKeyField(Address)


class Tag(BaseModel):
    tag = CharField(max_length=20)


class Product(BaseModel):
    name = CharField(max_length=30)
    description = TextField()
    price_per_unit = DecimalField(decimal_places=2, rounding='ROUND_HALF_UP')
    amount_in_stock = IntegerField()


class ProductTag(BaseModel):
    tag_id = ForeignKeyField(Tag)
    product_id = ForeignKeyField(Product)


class UsersOwnProducts(BaseModel):
    user_id = ForeignKeyField(User, backref='products')
    product_id = ForeignKeyField(Product)


class Transaction(BaseModel):
    buyer_id = ForeignKeyField(User)
    seller_id = ForeignKeyField(User)
    product_id = ForeignKeyField(Product)
    quantity = IntegerField()

