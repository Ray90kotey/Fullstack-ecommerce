from flask import Flask, jsonify, abort

app = Flask(__name__)

# Temporary in-memory data store
products = [
    {"id": 1, 
     "name": "Laptop", 
     "price": 999.99, 
     "Grade": "A"},
    {"id": 2, 
     "name": "Smartphone", 
     "price": 499.99, 
     "Grade": "A"},
    {"id": 3, 
     "name": "Headphones", 
     "price": 199.99,
     "Grade": "B"
     },
]

@app.route("/")
def home():
    return jsonify({
      "message": "ecommerce backend is running"
      })
  
@app.route("/api/products", methods=["GET"]) 
def get_products():
    return jsonify(products) 
   

@app.route("/api/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
  product = next((p for p in products if p["id"] == product_id), None)
  if product is None:
    abort(404)
  return jsonify(product)
  
if __name__ == "__main__":
    app.run(debug=True)