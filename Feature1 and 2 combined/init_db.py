from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from datetime import datetime

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["influencer_marketing"]

# Clear existing collections (for development)
db.influencers.drop()
db.brands.drop()
db.campaigns.drop()

# Create collections with validation
db.create_collection("influencers", validator={
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["handle", "password", "name"],
        "properties": {
            "handle": {"bsonType": "string", "pattern": "^@.+$"},
            "password": {"bsonType": "string"},
            "name": {"bsonType": "string"},
            "followers": {"bsonType": "int"},
            "topics": {"bsonType": "array"}
        }
    }
})

db.create_collection("brands", validator={
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["name", "password"],
        "properties": {
            "name": {"bsonType": "string"},
            "password": {"bsonType": "string"},
            "industry": {"bsonType": "string"}
        }
    }
})

db.create_collection("campaigns", validator={
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["brand", "influencer", "product", "rate", "status"],
        "properties": {
            "brand": {"bsonType": "string"},
            "influencer": {"bsonType": "string", "pattern": "^@.+$"},
            "product": {"bsonType": "string"},
            "rate": {"bsonType": "int", "minimum": 0},
            "status": {
                "bsonType": "string",
                "enum": ["pending", "approved", "completed", "rejected"]
            },
            "created_at": {"bsonType": "date"}
        }
    }
})

# Create indexes
db.influencers.create_index("handle", unique=True)
db.brands.create_index("name", unique=True)
db.campaigns.create_index("brand")
db.campaigns.create_index("influencer")

# Sample data
sample_influencers = [
    {
        "handle": "@fashionista",
        "password": generate_password_hash("influ123"),
        "name": "Emma Styles",
        "followers": 150000,
        "topics": ["Fashion", "Beauty"]
    },
    {
        "handle": "@techguru",
        "password": generate_password_hash("influ123"),
        "name": "Alex Tech",
        "followers": 200000,
        "topics": ["Technology", "Gadgets"]
    }
]

sample_brands = [
    {
        "name": "Nike",
        "password": generate_password_hash("brand123"),
        "industry": "Sportswear"
    },
    {
        "name": "Apple",
        "password": generate_password_hash("brand123"),
        "industry": "Technology"
    }
]

sample_campaigns = [
    {
        "brand": "Nike",
        "influencer": "@fashionista",
        "product": "Air Max Shoes",
        "rate": 1500,
        "status": "approved",
        "created_at": datetime.utcnow()
    },
    {
        "brand": "Apple",
        "influencer": "@techguru",
        "product": "iPhone 15",
        "rate": 3000,
        "status": "pending",
        "created_at": datetime.utcnow()
    }
]

# Insert sample data
db.influencers.insert_many(sample_influencers)
db.brands.insert_many(sample_brands)
db.campaigns.insert_many(sample_campaigns)

print("Database initialized with:")
print(f"- {db.influencers.count_documents({})} influencers")
print(f"- {db.brands.count_documents({})} brands")
print(f"- {db.campaigns.count_documents({})} campaigns")