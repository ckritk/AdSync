from pymongo import MongoClient


MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "post_scheduler"
COLLECTION_NAME = "scheduled_posts"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]
