from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import json_util

app = Flask(__name__)
client = MongoClient("mongodb://localhost:27017/")
db = client["influencer_db"]

@app.route("/api/update_price", methods=["POST"])
def update_price():
    data = request.json
    db.influencers.update_one(
        {"NAME": {"$regex": data["username"], "$options": "i"}},
        {"$set": {"MIN_PRICE": data["price"]}}
    )
    return jsonify({"status": "success"})

@app.route("/api/influencer")
def get_influencer_uname():
    data = request.json
    influencers = list(db.influencers.find({"NAME": {"$regex": data["username"], "$options": "i"}}))
    return json_util.dumps(influencers)


@app.route("/api/influencers")
def get_influencers():
    
    min_price = int(request.args.get("min_price", 0))
    influencers = list(db.influencers.find({"MIN_PRICE": {"$gte": min_price}}))
    return json_util.dumps(influencers)

if __name__ == "__main__":
    app.run(debug=True)