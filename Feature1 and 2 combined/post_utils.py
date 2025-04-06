from db import collection
from datetime import datetime
from bson.objectid import ObjectId

def save_post_to_db(platforms_with_types, caption, media_path, schedule_time):
    post = {
        "platforms": platforms_with_types,  
        "caption": caption,
        "media_path": media_path,
        "schedule_time": schedule_time.strftime("%Y-%m-%d %H:%M:%S"),
        "posted": False,
        "created_at": datetime.now()
    }
    collection.insert_one(post)




def fetch_all_posts():
    return list(collection.find())

def mark_post_as_posted(post_id):
    collection.update_one({"_id": ObjectId(post_id)}, {"$set": {"posted": True}})
