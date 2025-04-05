import pandas as pd
from pymongo import MongoClient
from werkzeug.security import generate_password_hash
import re

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["influencer_marketing"]

def clean_er(er_value):
    """Convert ER values to float"""
    try:
        if pd.isna(er_value) or er_value == "-":
            return None
        return float(str(er_value).replace("%", ""))
    except:
        return None

def clean_reach(reach_value):
    """Convert POTENTIAL REACH to integer"""
    try:
        if pd.isna(reach_value) or reach_value == "-":
            return None
        return float(str(reach_value).replace("M", "")) * 1_000_000
    except:
        return None

def split_name(full_name):
    """Split NAME into name and handle"""
    if pd.isna(full_name):
        return None, None
    parts = str(full_name).rsplit("@", 1)  # Split on last @
    name = parts[0].strip()
    handle = f"@{parts[1].strip()}" if len(parts) > 1 else None
    return name, handle

def clean_topics(topic_str):
    """Convert TOPIC OF INFLUENCE to array"""
    if pd.isna(topic_str):
        return []
    # Remove duplicates and standardize
    topics = list(set(t.strip() for t in re.split(r"\s+and\s+|\s+", str(topic_str)) if t.strip()))

    cleaned_topics = []
    for topic in topics:
        lower_topic = str(topic).lower()
        if lower_topic =="&":
            continue
        if lower_topic in ["public", "figure", "public figure"]:
            if "celebrity" not in [t.lower() for t in cleaned_topics]:
                cleaned_topics.append("Celebrity")
        else:
            cleaned_topics.append(topic)
    return cleaned_topics

# Load CSV
df = pd.read_csv("instagram_data_all-countries.csv")

# Transform data
df[["name", "handle"]] = df["NAME"].apply(lambda x: pd.Series(split_name(x)))
df["password"] = generate_password_hash("12345678")  # Temporary password
df["ER"] = df["ER"].apply(clean_er)
df["POTENTIAL_REACH"] = df["POTENTIAL REACH"].apply(clean_reach)
df["topics"] = df["TOPIC OF INFLUENCE"].apply(clean_topics)
df["primary_topic"] = df["topics"].apply(lambda x: x[0] if x else None)
df["MIN_PRICE"] = 0  # Initialize
df["Platform"] = "Instagram"

# Prepare for MongoDB
records = []
for _, row in df.iterrows():
    record = {
        "handle": row["handle"],
        "name": row["name"],
        "password": row["password"],
        "FOLLOWERS": float(row["FOLLOWERS"].replace("M", "")) * 1_000_000 if isinstance(row["FOLLOWERS"], str) else row["FOLLOWERS"],
        "ER": row["ER"],
        "COUNTRY": row["COUNTRY"],
        "MIN_PRICE": row["MIN_PRICE"],
        "Platform": row["Platform"],
        "POTENTIAL_REACH": row["POTENTIAL_REACH"],
        "primary_topic": row["primary_topic"],
        "topics": row["topics"]
    }
    records.append(record)

# Update MongoDB (preserve existing _ids)
collection = db.influencers
result = collection.insert_many(records)
print(f"Inserted {len(result.inserted_ids)} influencers")

# Create indexes
collection.create_index("handle", unique=True)
collection.create_index("primary_topic")
collection.create_index("topics")
print("Indexes created")
