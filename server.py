from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient("mongodb+srv://joshuaug22ec:LZElLjNBdgr0bzjZ@esp.wptyr.mongodb.net/?retryWrites=true&w=majority&appName=esp")
db = client["esp"]
collection = db["joshu"]

@app.route('/data', methods=['POST'])
def receive_data():
    data = request.json
    print("Received:", data)  # Debugging
    if data:
        collection.insert_one(data)
        return jsonify({"message": "Data received successfully"}), 201
    return jsonify({"error": "No data received"}), 400

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
