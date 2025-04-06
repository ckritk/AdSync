import time
from datetime import datetime
from db import collection
from bson.objectid import ObjectId
from post_utils import mark_post_as_posted
from google_drive_utils import upload_to_drive
import requests


FB_PAGE_ID = ""
FB_ACCESS_TOKEN = ""
IG_USER_ID = ""
IG_ACCESS_TOKEN = ""

def post_to_instagram(image_url, caption, ig_user_id, access_token):
    print(f"📤 Creating media container for Instagram...")

    create_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media"
    payload = {
        'image_url': image_url,
        'caption': caption,
        'access_token': access_token
    }
    res = requests.post(create_url, data=payload)
    result = res.json()
    print("📦 Creation response:", result)

    creation_id = result.get("id")
    if not creation_id:
        print("❌ Failed to create media. Error:", result)
        return False

    print(f"🚀 Publishing media...")
    publish_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media_publish"
    publish_payload = {
        'creation_id': creation_id,
        'access_token': access_token
    }
    publish_res = requests.post(publish_url, data=publish_payload)
    print("📣 Publish response:", publish_res.json())

    return publish_res.ok

# --- Post to Facebook ---
def post_to_facebook(image_url, caption, page_id, access_token):
    print(f"📤 Creating photo post for Facebook Page...")

    post_url = f"https://graph.facebook.com/{page_id}/photos"
    payload = {
        'url': image_url,
        'caption': caption,
        'access_token': access_token
    }

    res = requests.post(post_url, data=payload)
    result = res.json()
    print("📣 Facebook post response:", result)

    return 'id' in result
