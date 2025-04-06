# similar_influencers.py

import streamlit as st
from knn_model import InfluencerMatcher
from pymongo import MongoClient
from bson import ObjectId

def show():
    st.title("🔍 Find Similar Influencers")

    # Connect to DB
    client = MongoClient("mongodb://localhost:27017/")
    db = client["influencer_marketing"]
    collection = db["influencers"]
    
    # Fetch influencer handles for dropdown
    all_influencers = list(collection.find({}, {"handle": 1}))
    options = {f"{inf['handle']}": str(inf["_id"]) for inf in all_influencers}
    
    selected_handle = st.selectbox("Choose an influencer:", list(options.keys()))

    if selected_handle:
        matcher = InfluencerMatcher(k=5)
        similar = matcher.find_similar(ObjectId(options[selected_handle]))

        st.write(f"### 🔗 Similar to {selected_handle}")
        for s in similar:
            st.markdown(f"**{s['handle']}** ({s['name']})")
            st.write(f"- Followers: {s['FOLLOWERS']}")
            st.write(f"- ER: {s['ER']}")
            st.write(f"- Topics: {', '.join(s['topics'])}")
            st.write(f"- Country: {s['COUNTRY']}")
            st.write(f"- Platform: {s['Platform']}")
            st.markdown("---")

    st.button("⬅ Back to Dashboard", on_click=lambda: st.session_state.update({"page": "brand_dash"}))
