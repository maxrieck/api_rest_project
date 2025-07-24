# REST API Project

This project is a simple RESTful API built with Flask, SQLAlchemy, and Marshmallow for managing customers, products, and orders.

## How It Works

The application uses Flask to handle HTTP requests and responses, providing a set of API endpoints for interacting with customer, product, and order data. SQLAlchemy is used as the ORM (Object Relational Mapper) to define models and interact with a MySQL database, while Marshmallow handles serialization and validation of data.

When you send a request to an endpoint (for example, to add a customer or get a list of products), Flask receives the request and passes the data to the appropriate function. The function uses SQLAlchemy to query or update the database, and Marshmallow to convert the database objects to JSON for the response. For listing customers and products, the API supports pagination, so you can request specific pages of results using query parameters.

All data is sent and received in JSON format, making it easy to use this API with web or mobile frontends, or for testing with tools like Postman.

## Features
- Create, read, update, and delete (CRUD) customers, products, and orders
- Add and remove products from orders
- Pagination support for listing customers and products
- JSON serialization using Marshmallow schemas

## Requirements
- Python 3.8+
- Flask
- Flask-SQLAlchemy
- Flask-Marshmallow
- Marshmallow
- MySQL database

## Setup
1. Clone the repository or copy the project files.
2. Install dependencies:
   ```sh
   pip install flask flask_sqlalchemy flask_marshmallow marshmallow mysql-connector-python
   ```
3. Update the MySQL connection string in `main.py` if needed.
4. Run the application:
   ```sh
   python main.py
   ```

## API Endpoints

### Customers
- `POST /customers` — Add a new customer
- `GET /customers` — List customers (supports `page` and `per_page` query params)
- `GET /customers/<id>` — Get a specific customer
- `PUT /customers/<id>` — Update a customer
- `DELETE /customers/<id>` — Delete a customer

### Products
- `POST /products` — Add a new product
- `GET /products` — List products (supports `page` and `per_page` query params)
- `GET /products/<id>` — Get a specific product
- `PUT /products/<id>` — Update a product
- `DELETE /products/<id>` — Delete a product

### Orders
- `POST /orders` — Create a new order
- `GET /orders` — List all orders
- `GET /orders/<id>` — Get a specific order
- `PUT /orders/<order_id>/add_product/<product_id>` — Add a product to an order
- `DELETE /orders/<order_id>/remove_product/<product_id>` — Remove a product from an order
- `DELETE /orders/<id>` — Delete an order

## Pagination Example
To get the second page of products with 5 per page:
```
GET /products?page=2&per_page=5
```

## Notes
- Make sure your MySQL server is running and accessible.
- The database tables are created automatically on first run.

---
