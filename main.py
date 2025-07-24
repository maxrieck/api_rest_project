from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from sqlalchemy import ForeignKey, Table, Column, String, Integer, select, delete
from marshmallow import ValidationError, fields
from typing import List, Optional
from datetime import date


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql+mysqlconnector://root:Donyseus%401@localhost/rest_api_project"
)


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(app, model_class=Base)
ma = Marshmallow(app)


# <============= Models ===============================>


class Customer(Base):

    __tablename__ = "Customer"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(200), nullable=False)
    email: Mapped[str] = mapped_column(db.String(200))
    address: Mapped[str] = mapped_column(db.String(250))

    orders: Mapped[List["Orders"]] = db.relationship(back_populates="customer")


# Assocition Table for Orders and Products
order_products = db.Table(
    "Order_Products",
    Base.metadata,
    db.Column("order_id", db.ForeignKey("orders.id")),
    db.Column("product_id", db.ForeignKey("products.id")),
)


class Orders(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_date: Mapped[date] = mapped_column(db.Date, nullable=False)

    customer_id: Mapped[int] = mapped_column(db.ForeignKey("Customer.id"))

    customer: Mapped["Customer"] = db.relationship(back_populates="orders")

    products: Mapped[List["Products"]] = db.relationship(
        secondary=order_products, back_populates="orders"
    )


class Products(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column(db.String(250), nullable=False)
    price: Mapped[float] = mapped_column(db.Float, nullable=False)
    orders: Mapped[List["Orders"]] = db.relationship(
        secondary=order_products, back_populates="products"
    )


with app.app_context():
    db.create_all()


# <============= Schemas ===============================>


class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer


class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Products


class OrdersSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Orders
        include_fk = True


customer_schema = CustomerSchema()
customers_schmea = CustomerSchema(many=True)

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

order_schema = OrdersSchema()
orders_schema = OrdersSchema(many=True)


# <============== Routes ===============================>


@app.route("/")
def home():
    return "Home"


# ========== Customer Routes ========>

# Creates new customers
@app.route("/customers", methods=["POST"])
def add_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_customer = Customer(
        name=customer_data["name"],
        email=customer_data["email"],
        address=customer_data["address"],
    )

    db.session.add(new_customer)
    db.session.commit()

    return (
        jsonify(
            {
                "Message": "New Customer added successfully!",
                "customer": customer_schema.dump(new_customer),
            }
        ),
        201,
    )


# View all Products
@app.route("/customers", methods=["GET"])
def get_customers():
    page = request.args.get("page", 1, type=int)   # sets default page value to 1
    per_page = request.args.get("per_page", 5, type=int)   #sets limit of 5 products per page
    # paginates the products based the page and per_page variables 
    # use " customers?page=1&per_page=5 " formaat on Postman to view pages
    pagination = db.paginate(db.select(Customer), page=page, per_page=per_page, error_out=False)
    customers = pagination.items
    return jsonify({
        "customers": customers_schmea.dump(customers),
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": pagination.page
    }), 200


# View specific Customer
@app.route("/customers/<int:id>", methods=["GET"])
def get_customer(id):
    customer = db.session.get(Customer, id)

    if customer is None:
        return jsonify({"Error": "Customer not found"}), 404

    return customer_schema.jsonify(customer), 200


# Update customer
@app.route("/customers/<int:id>", methods=["PUT"])
def update_customer(id):
    customer = db.session.get(Customer, id)

    if not customer:
        return jsonify({"message": "Invalid customer id"}), 400

    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    customer.name = customer_data["name"]
    customer.email = customer_data["email"]
    customer.address = customer_data["address"]

    db.session.commit()
    return customer_schema.jsonify(customer), 200


# Delete customer
@app.route("/customers/<int:id>", methods=["DELETE"])
def delete_customer(id):
    customer = db.session.get(Customer, id)

    if not customer:
        return jsonify({"message": "Invalid customer id"}), 400

    db.session.delete(customer)
    db.session.commit()

    return jsonify({"message": f"successfully deleted user {id}"}), 200



# ========== Product Routes ========>

# Create product
@app.route("/products", methods=["POST"])
def create_product():
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    new_product = Products(
        product_name=product_data["product_name"], price=product_data["price"]
    )

    db.session.add(new_product)
    db.session.commit()

    return (
        jsonify(
            {
                "Message": "New Product added!",
                "customer": product_schema.dump(new_product),
            }
        ),
        201,
    )

# View all Products
@app.route("/products", methods=["GET"])
def get_products():
    page = request.args.get("page", 1, type=int)   # sets default page value to 1
    per_page = request.args.get("per_page", 5, type=int)   #sets limit of 5 products per page
    # paginates the products based the page and per_page variables 
    # use " products?page=1&per_page=5 " formaat on Postman to view pages
    pagination = db.paginate(db.select(Products), page=page, per_page=per_page, error_out=False)
    products = pagination.items
    return jsonify({
        "products": products_schema.dump(products),
        "total": pagination.total,
        "pages": pagination.pages,
        "current_page": pagination.page
    }), 200


# View specific Product
@app.route("/products/<int:id>", methods=["GET"])
def get_product(id):
    product = db.session.get(Products, id)

    if product is None:
        return jsonify({"Error": "Product not found"}), 404

    return product_schema.jsonify(product), 200


# Update Product
@app.route("/products/<int:id>", methods=["PUT"])
def update_product(id):
    product = db.session.get(Products, id)

    if not product:
        return jsonify({"message": "Invalid product id"}), 400

    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    product.product_name = product_data["product_name"]
    product.price = product_data["price"]

    db.session.commit()
    return customer_schema.jsonify(product), 200


# Delete Product
@app.route("/products/<int:id>", methods=["DELETE"])
def delete_product(id):
    product = db.session.get(Products, id)

    if product is None:
        return jsonify({"message": "Invalid product id"}), 400

    db.session.delete(product)
    db.session.commit()

    return jsonify({"message": f"successfully deleted product {id}"}), 200



# ========== Order Routes ========>

# Create an Order
@app.route("/orders", methods=["POST"])
def add_order():
    try:
        order_data = order_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    customer = db.session.get(Customer, order_data["customer_id"])

    if customer:
        new_order = Orders(
            order_date=order_data["order_date"], customer_id=order_data["customer_id"]
        )

        db.session.add(new_order)
        db.session.commit()

        return (
            jsonify(
                {"Message": "New order placed!", "order": order_schema.dump(new_order)}
            ),
            201,
        )
    else:
        return jsonify({"message": "Invalid customer id"}), 400


# adds specific Products to specific Order
@app.route("/orders/<int:order_id>/add_product/<int:product_id>", methods=["PUT"])
def add_product(order_id, product_id):
    order = db.session.get(Orders, order_id)
    product = db.session.get(Products, product_id)

    if order and product:
        if product not in order.products:
            order.products.append(product)
            db.session.commit()
            return jsonify({"Message": "Successfully added item to order."}), 200
        else:
            return jsonify({"Message": "Item is already included in this order."}), 400
    else:
        return jsonify({"Message": "Invalid order id or product id."}), 400


# removes specific Products from  specific Order
@app.route("/orders/<int:order_id>/remove_product/<int:product_id>", methods=["DELETE"])
def remove_product(order_id, product_id):
    order = db.session.get(Orders, order_id)
    product = db.session.get(Products, product_id)

    if order and product:
        if product in order.products:
            order.products.remove(product)
            db.session.commit()
            return jsonify({"Message": "Successfully deleted item from order."}), 200
        else:
            return jsonify({"Message": "Item isn't included in this order."}), 400
    else:
        return jsonify({"Message": "Invalid order id or product id."}), 400

# view All Orders
@app.route("/orders", methods=["GET"])
def get_orders():
    query = select(Orders)
    orders = db.session.execute(query).scalars().all()

    return orders_schema.jsonify(orders), 200

# view Specific Order
@app.route("/orders/<int:id>", methods=["GET"])
def get_order(id):
    order = db.session.get(Orders, id)

    if order is None:
        return jsonify({"Error": "Order not found"}), 404

    return order_schema.jsonify(order), 200

# deletes entire Order
@app.route("/orders/<int:id>", methods=["DELETE"])
def delete_order(id):
    order = db.session.get(Orders, id)

    if order is None:
        return jsonify({"message": "Invalid order id"}), 400

    db.session.delete(order)
    db.session.commit()

    return jsonify({"message": f"successfully order product {id}"}), 200

# <=======================================>


if __name__ == "__main__":
    app.run(debug=True)
