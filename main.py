# Do not modify these lines
__winc_id__ = "d7b474e9b3a54d23bca54879a4f1855b"
__human_name__ = "Betsy Webshop"

import sys
from models import data, User, Address, UserAddresses, Tag, Product, ProductTag, UsersOwnProducts, Transaction, fn
from fuzzywuzzy import process
import os
from texttable import Texttable


def search(term):
    products_for_search = []
    descriptions_for_search = []
    for product in Product.select():
        products_for_search.append(product.name)
        descriptions_for_search.append(product.description)
    product_terms_to_search = process.extract(term, products_for_search)
    descriptions_to_search = process.extract(term, descriptions_for_search)
    products = []
    for product in product_terms_to_search:
        if product[1] > 75:
            if product[0] not in products:
                products.append(product[0])
    for description in descriptions_to_search:
        if description[1] > 50:
            product_description = Product.get(Product.description == description[0])
            product_name = product_description.name
            if product_name not in products:
                products.append(product_name)
    if not products:
        print('I cant find that product!')
        return False
    else:
        t = Texttable()
        t.add_row(["Product_name"])
        for product in products:
            if product:
                t.add_row([product])
        print(t.draw())
        return True


def list_user_products(user_id):
    user_products = []
    for user_product in Product.select().join(UsersOwnProducts).join(User).where(User.id == user_id):
        user_products.append(user_product)
    if not user_products:
        print('This User has no products')
        return False
    else:
        t = Texttable()
        t.add_row(['Product', 'Description'])
        for product in user_products:
            t.add_row([str(product.name).title(), str(product.description)])
        print(t.draw())
        return True


def list_products_per_tag(tag):
    found_products = []
    for product in Product.select().join(ProductTag).join(Tag).where(fn.LOWER(Tag.tag) == tag.lower()):
        found_products.append(product)
    if not found_products:
        print('I Cant Find Your Product')
        return False
    else:
        t = Texttable()
        t.add_row(['Product', 'Description'])
        for product in found_products:
            t.add_row([str(product.name).title(), str(product.description)])
        print(t.draw())
        return True


def add_product_to_catalog(user_id, product, tag_name):
    if not Tag.select().where(Tag.tag == tag_name).exists():
        Tag.create(tag=tag_name)
        tag = Tag.get(Tag.tag == tag_name)
        Product.create(name=product[0], description=product[1], price_per_unit=product[2], amount_in_stock=product[3])
        product_id = Product.get(Product.name == product[0])
        ProductTag.create(tag_id=tag, product_id=product_id)
    else:
        tag = Tag.get(Tag.tag == tag_name)
        Product.create(name=product[0], description=product[1], price_per_unit=product[2], amount_in_stock=product[3])
        product_id = Product.get(Product.name == product[0])
        ProductTag.create(tag_id=tag, product_id=product_id)
    user = User.get(User.id == user_id)
    new_product = Product.get(Product.name == product[0])
    UsersOwnProducts.create(user_id=user, product_id=new_product)
    print(f"Status: Done adding Product {product[0]} to catalog")
    return True


def remove_product(product_id):
    Product.delete_by_id(product_id)
    UsersOwnProducts.delete().where(UsersOwnProducts.product_id == product_id).execute()
    ProductTag.delete().where(ProductTag.product_id == product_id).execute()
    print(f"Product: {product_id}, Status: PRODUCT REMOVED")
    return True


def update_stock(product_id, new_quantity):
    Product.update(amount_in_stock=new_quantity).where(Product.id == product_id).execute()
    print(f"Product: {product_id}, Quantity: {new_quantity}, Status: STOCK UPDATE")
    return True


def purchase_product(product_id, buyer_id, quantity):
    product = Product.get(Product.id == product_id)
    buyer = User.get(User.id == buyer_id)
    seller = User.select().join(UsersOwnProducts).join(Product).where(Product.id == product_id)
    if quantity > product.amount_in_stock:
        print('This Product Has been Sold Out!')
        return False
    elif quantity == product.amount_in_stock:
        Transaction.create(buyer_id=buyer, seller_id=seller, product_id=product, quantity=quantity)
        update_stock(product_id, 0)
        UsersOwnProducts.delete().where(UsersOwnProducts.product_id == product_id).execute()
        print("Sale: Success, status: This Product Has Now Been Sold Out!!")
        return True
    else:
        Transaction.create(buyer_id=buyer, seller_id=seller, product_id=product, quantity=quantity)
        new_stock = product.amount_in_stock - quantity
        update_stock(product_id, new_stock)
        print("Sale: Success, status: Sold with Success!")
        return True


def populate_test_database():
    data.connect()
    models = [User, Address, UserAddresses, Tag, Product, ProductTag, UsersOwnProducts, Transaction]
    data.create_tables(models)
    user_details = ['Alex', 'Ferry', 'Willem', 'Alexander', 'Melvin']
    for user in user_details:
        User.create(name=user)
    print(f'{len(user_details)} Users added to database!')
    addresses = [
        ('street_name_one', 1, '', '3204XL', 'Spijkenisse', 'The Netherlands'),
        ('street_name_two', 34, '', '1334 BC', 'Almere-Buiten', 'The Netherlands'),
        ('street_name_three', 65, 'A4', '3077EP', 'Rotterdam', 'The Netherlands'),
        ('street_name_four', 8, '', '1335JT', 'Almere-Oostvaarders', 'The Netherlands'),
        ('street_name_five', 136, 'F2', '8232DL', 'Zwolle', 'The Netherlands'),
        ('street_name_six', 4, 'B4', '5814GT', 'Eindhoven', 'The Netherlands'),
        ('street_name_seven', 18, 'G5', '3202XL', 'Spijkenisse', 'The Netherlands')
    ]
    Address.insert_many(addresses,
                        fields=[Address.street, Address.number, Address.number_addition, Address.zip_code, Address.city,
                                Address.country]).execute()
    print(f'{len(addresses)} Addresses added to database!')
    user_addresses = [
        (1, 1, 1),
        (2, 2, 2),
        (3, 3, 4),
        (4, 5, 5),
        (5, 6, 7)
    ]
    for user_id, home_address_id, billing_address_id in user_addresses:
        user = User.get(User.id == user_id)
        home_address = Address.get(Address.id == home_address_id)
        billing_address = Address.get(Address.id == billing_address_id)
        UserAddresses.create(user_id=user, home_address_id=home_address, billing_address_id=billing_address)
    print(f'{len(user_addresses)} UsersAdresses added to database!')
    tags = ['Schoenen', 'TrainingsPak', 'BodyWarmer']
    for tag in tags:
        Tag.create(tag=tag)
    print(f'{len(tags)} Tags added to database!')
    products = [
        ('Nike Schoenen', 'Hele mooie Nike schoenen!', 250.99, 100),
        ('AZ TrainingsPak', 'Prachtige TrainingsPak!', 150.00, 100),
        ('Ajax TrainingsPak', 'Prachtige TrainingsPak!', 150.00, 100),
        ('Nike BodyWarmer', 'Nieuwste Nike BodyWarmer!', 320.00, 100)
    ]
    for name, description, price_per_unit, amount_in_stock in products:
        Product.create(name=name, description=description, price_per_unit=price_per_unit,
                       amount_in_stock=amount_in_stock)
    print(f'{len(products)} Products added to database!')
    product_tags = [
        (1, 1),
        (2, 2),
        (3, 2),
        (4, 3)
    ]
    for product, tag in product_tags:
        product_id = Product.get(Product.id == product)
        tag_id = Tag.get(Tag.id == tag)
        ProductTag.create(product_id=product_id, tag_id=tag_id)
    print(f'{len(product_tags)} ProductTags added to database!')
    user_own_products = [
        (1, 1),
        (1, 3),
        (3, 2),
        (5, 4)
    ]
    for user, product in user_own_products:
        user_id = User.get(User.id == user)
        product_id = Product.get(Product.id == product)
        UsersOwnProducts.create(user_id=user_id, product_id=product_id)
    print(f'{len(user_own_products)} UserOwnProducts added to database!')
    data.close()
    return True


def delete_database():
    cwd = os.getcwd()
    try:
        database_path = os.path.join(cwd, "betsy_boop.db")
        if os.path.exists(database_path):
            os.remove(database_path)
            return True
        return False
    except (PermissionError, Exception):
        sys.exit("Hmm..!!")


'''uncomment to Test and run populate_test_database first to create and fill up database with test info'''
# populate_test_database()
# search("trainingspak")
# list_user_products(1)
# list_products_per_tag("schoenen")
# purchase_product(3, 4, 1)
# add_product_to_catalog("2", ["Samsung s23", "De beste Telefoon van het Jaar", 1295.63, 450], tag_name="Telefoon")
# remove_product(4)
# update_stock(1, 500)
# delete_database()
