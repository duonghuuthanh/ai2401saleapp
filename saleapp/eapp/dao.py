from eapp.models import Category, Product, User, Receipt, ReceiptDetails
from eapp import app, db
import hashlib
import cloudinary.uploader
from flask_login import current_user
from sqlalchemy import func


def load_categories():
    return Category.query.order_by('id').all()

def load_products(kw=None, cate_id=None, page=1):
    query = Product.query

    if kw:
        query = query.filter(Product.name.contains(kw))

    if cate_id:
        query = query.filter(Product.category_id==int(cate_id))

    page_size = app.config['PAGE_SIZE']
    start = (page - 1) * page_size
    query = query.slice(start, start + page_size)

    return query.all()

def count_products():
    return Product.query.count()

def authorize(username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    return User.query.filter(User.username.__eq__(username.strip()), User.password.__eq__(password)).first()

def get_user_by_id(id):
    return User.query.get(id)

def add_user(name, username, password, avatar):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u = User(name=name, username=username, password=password, avatar=avatar)

    if avatar:
        res = cloudinary.uploader.upload(avatar)
        print(res)
        u.avatar = res['secure_url']

    db.session.add(u)
    db.session.commit()


def add_receipt(cart):
    if cart:
        r = Receipt(user=current_user)
        db.session.add(r)

        for c in cart.values():
            d = ReceiptDetails(quantity=c['quantity'], price=c['price'], product_id=c['id'], receipt=r)
            db.session.add(d)

        db.session.commit()


def count_products_by_cate():
    return (db.session.query(Category.id, Category.name, func.count(Product.id))
            .join(Product, Product.category_id==Category.id, isouter=True).group_by(Category.id).all())


def cal_revenue_by_product(kw=None):
    query = (db.session.query(Product.id, Product.name, func.sum(ReceiptDetails.quantity * ReceiptDetails.price))
             .join(ReceiptDetails, ReceiptDetails.product_id==Product.id)).group_by(Product.id)

    if kw:
        query = query.filter(Product.name.contains(kw))

    return query.all()

def cal_revenue_by_time(time, year):
    query = (db.session.query(func.extract(time, Receipt.created_date), func.sum(ReceiptDetails.quantity * ReceiptDetails.price))
             .join(ReceiptDetails, ReceiptDetails.receipt_id==Receipt.id).filter(func.extract('year', Receipt.created_date)==year)
             .group_by(func.extract(time, Receipt.created_date)))

    return query.all()


if __name__ == '__main__':
    with app.app_context():
        print(cal_revenue_by_time(2026))
