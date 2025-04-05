import streamlit as st
from pymongo import MongoClient

def show():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["influencer_marketing"]
    
    # Header
    st.title(f"👋 Hello, {st.session_state.influencer['name']}")
    st.write("---")
    
    # Profile Section
    with st.expander("📝 Edit Profile", expanded=True):
        with st.form("profile_form"):
            # Editable fields
            new_name = st.text_input("Name", value=st.session_state.influencer.get("name", ""))
            new_price = st.number_input(
                "Minimum Price ($)", 
                min_value=0,
                value=st.session_state.influencer.get("MIN_PRICE", 0)
            )
            
            # Display non-editable info
            st.text(f"Handle: {st.session_state.influencer['handle']}")
            st.text(f"Followers: {st.session_state.influencer.get('FOLLOWERS', 0):,}")
            
            if st.form_submit_button("Save Changes"):
                update_profile(new_name, new_price)
    
    # Logout button
    if st.button("Logout"):
        st.session_state.influencer = None
        st.session_state.page = "home"
        st.rerun()

def update_profile(name, price):
    """Update influencer profile in database"""
    client = MongoClient("mongodb://localhost:27017/")
    db = client["influencer_marketing"]
    
    db.influencers.update_one(
        {"_id": st.session_state.influencer["_id"]},
        {"$set": {
            "name": name,
            "MIN_PRICE": price
        }}
    )
    st.success("Profile updated successfully!")
    st.session_state.influencer = db.influencers.find_one({"_id": st.session_state.influencer["_id"]})