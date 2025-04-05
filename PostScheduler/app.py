import streamlit as st
from datetime import datetime
import os
import pandas as pd
from post_utils import save_post_to_db, fetch_all_posts
from google_drive_utils import upload_to_drive


st.set_page_config(page_title="Post Scheduler", layout="wide")
st.title("📆 Automated Post Scheduler")


platform_post_types = {
    "Facebook": ["Post", "Story", "Reel"],
    "Instagram": ["Post", "Story", "Reel"],
    "YouTube": ["Video", "Short"],
    "Twitter": ["Post"],
    "LinkedIn": ["Post"]
}


selected_platforms = st.multiselect("Select Platforms", list(platform_post_types.keys()))
platform_post_type_pairs = []

for platform in selected_platforms:
    post_type = st.selectbox(f"Select post type for {platform}", platform_post_types[platform], key=platform)
    platform_post_type_pairs.append({"platform": platform, "type": post_type})

caption = st.text_area("Caption")
media_file = st.file_uploader("Upload Media", type=["jpg", "png", "mp4"])


if 'selected_date' not in st.session_state:
    st.session_state.selected_date = datetime.now().date()
if 'selected_time' not in st.session_state:
    st.session_state.selected_time = datetime.now().time()

date = st.date_input("Select Date", value=st.session_state.selected_date)
time = st.time_input("Select Time", value=st.session_state.selected_time)
st.session_state.selected_date = date
st.session_state.selected_time = time

schedule_time = datetime.combine(date, time)


if st.button("Schedule Post"):
    if not media_file:
        st.warning("⚠️ Please upload a media file.")
    elif not platform_post_type_pairs:
        st.warning("⚠️ Please select at least one platform.")
    else:
        os.makedirs("media", exist_ok=True)
        media_path = os.path.join("media", media_file.name)

     
        with open(media_path, "wb") as f:
            f.write(media_file.getbuffer())


        drive_link = upload_to_drive(media_path)

 
        os.remove(media_path)

    
        save_post_to_db(platform_post_type_pairs, caption, drive_link, schedule_time)
        st.success("✅ Post scheduled successfully!")


posts = fetch_all_posts()
if posts:
    df = pd.DataFrame(posts)
    df['_id'] = df['_id'].astype(str)

   
    def format_platforms(platforms):
        return ", ".join([f"{p['platform']} ({p['type']})" for p in platforms])

    df['platforms'] = df['platforms'].apply(format_platforms)

    st.subheader("📋 Scheduled Posts")
    st.dataframe(df)
else:
    st.info("No scheduled posts found.")
