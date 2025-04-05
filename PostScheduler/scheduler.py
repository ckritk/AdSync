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


# --- Scheduler Loop ---
def run_scheduler():
    print("⏳ Scheduler started. Watching for scheduled posts...")

    while True:
        posts = list(collection.find({"posted": False}))
        for post in posts:
            schedule_time = datetime.strptime(post['schedule_time'], "%Y-%m-%d %H:%M:%S")
            if datetime.now() >= schedule_time:
                print(f"🕐 Time to post: {post['caption'][:30]}...")
                media_url = post['media_path']
                print("📂 Using uploaded media URL:", media_url)

                for entry in post.get("platforms", []):
                    platform = entry.get("platform")
                    post_type = entry.get("type", "Post")

                    if platform == "Instagram":
                        success = post_to_instagram(media_url, post['caption'], IG_USER_ID, IG_ACCESS_TOKEN)
                        if success:
                            print(f"✅ Posted to Instagram as {post_type}")
                        else:
                            print(f"❌ Failed to post to Instagram")

                    elif platform == "Facebook":
                        success = post_to_facebook(media_url, post['caption'], FB_PAGE_ID, FB_ACCESS_TOKEN)
                        if success:
                            print(f"✅ Posted to Facebook as {post_type}")
                        else:
                            print(f"❌ Failed to post to Facebook")

                mark_post_as_posted(post['_id'])
                print("✅ Marked as posted in MongoDB.\n")

        time.sleep(30)


# --- Run ---
if __name__ == "__main__":
    run_scheduler()
 
