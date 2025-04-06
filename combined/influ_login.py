import streamlit as st
from pymongo import MongoClient
from werkzeug.security import check_password_hash

def show():
    st.title("Influencer Login")
    
    # Simple login form
    handle = st.text_input("Your Instagram Handle (e.g., @username)")
    password = st.text_input("Password", type="password")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("Login"):
            authenticate(handle, password)
    with col2:
        if st.button("Back to Home"):
            st.session_state.page = "home"
            st.rerun()

def authenticate(handle, password):
    """Verify influencer credentials"""
    client = MongoClient("mongodb://localhost:27017/")
    db = client["influencer_marketing"]
    
    influencer = db.influencers.find_one({"handle": handle.lower()})
    
    if influencer and check_password_hash(influencer["password"], password):
        st.session_state.influencer = influencer
        st.session_state.page = "influencer_dashboard"
        st.rerun()
    else:
        st.error("Invalid handle or password")