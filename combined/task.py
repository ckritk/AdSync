from celery_app import app
from datetime import datetime
from db import collection
from post_utils import mark_post_as_posted
from scheduler import post_to_facebook, post_to_instagram
from scheduler import FB_PAGE_ID, FB_ACCESS_TOKEN, IG_USER_ID, IG_ACCESS_TOKEN

@app.task
def check_and_post():
    print("🔍 Checking for scheduled posts...")
    posts = list(collection.find({"posted": False}))
    for post in posts:
        schedule_time = datetime.strptime(post['schedule_time'], "%Y-%m-%d %H:%M:%S")
        if datetime.now() >= schedule_time:
            print(f"🕐 Time to post: {post['caption'][:30]}...")
            media_url = post['media_path']
            for entry in post.get("platforms", []):
                platform = entry.get("platform")
                post_type = entry.get("type", "Post")

                if platform == "Instagram":
                    success = post_to_instagram(media_url, post['caption'], IG_USER_ID, IG_ACCESS_TOKEN)
                    print(f"{'✅' if success else '❌'} Instagram {post_type}")
                elif platform == "Facebook":
                    success = post_to_facebook(media_url, post['caption'], FB_PAGE_ID, FB_ACCESS_TOKEN)
                    print(f"{'✅' if success else '❌'} Facebook {post_type}")

            mark_post_as_posted(post['_id'])
            print("✅ Marked as posted")
