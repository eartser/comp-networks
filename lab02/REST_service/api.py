from flask import Flask
from flask_restful import Resource, Api, reqparse

app = Flask(__name__)
api = Api(app)
parser = reqparse.RequestParser()

PRODUCTS = {}


class ProductsList(Resource):
    def get(self):
        return PRODUCTS

    def post(self):
        parser.add_argument("name")
        parser.add_argument("description")
        args = parser.parse_args()
        product_id = int(max(PRODUCTS.keys(), default=0)) + 1
        product_id = '%i' % product_id
        PRODUCTS[product_id] = {
            "name": args["name"],
            "description": args["description"],
        }
        return PRODUCTS[product_id], 201


class Product(Resource):
    def get(self, product_id):
        if product_id not in PRODUCTS:
            return "Not found", 404
        else:
            return PRODUCTS[product_id]

    def put(self, product_id):
        parser.add_argument("name")
        parser.add_argument("description")
        args = parser.parse_args()
        if product_id not in PRODUCTS:
            return "Not found", 404
        product = PRODUCTS[product_id]
        PRODUCTS[product_id] = {
            "name": args["name"] if args["name"] is not None else product["name"],
            "description": args["description"] if args["description"] is not None else product["description"],
        }
        return PRODUCTS[product_id], 201

    def delete(self, product_id):
        if product_id not in PRODUCTS:
            return "Not found", 404
        else:
            del PRODUCTS[product_id]
            return '', 204


api.add_resource(ProductsList, '/products/')
api.add_resource(Product, '/products/<product_id>')

if __name__ == "__main__":
    app.run(debug=True)
