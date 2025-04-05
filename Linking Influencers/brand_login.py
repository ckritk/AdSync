# brand_login.py
import streamlit as st
from pymongo import MongoClient
from werkzeug.security import check_password_hash, generate_password_hash

def show_signup():
    st.title("Brand Signup")
    
    with st.form("signup_form"):
        username = st.text_input("Brand Username")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        submitted = st.form_submit_button("Create Account")
        
        if submitted:
            if password != confirm_password:
                st.error("Passwords don't match!")
                return
            if len(password) < 8:
                st.error("Password must be ≥8 characters")
                return
            
            client = MongoClient("mongodb://localhost:27017/")
            db = client["influencer_marketing"]
            
            if db.brands.find_one({"username": username}):
                st.error("Username taken!")
                return
            
            db.brands.insert_one({
                "username": username,
                "password": generate_password_hash(password),
                "campaigns": []
            })
            
            st.success("Account created! Please login.")
            st.session_state.page = "brand_login"  # Switch to login tab

def show():
    st.title("Brand Portal")
    
    login_tab, signup_tab = st.tabs(["Login", "Signup"])
    
    with login_tab:
        name = st.text_input("Brand Name")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            authenticate(name, password)
        
        if st.button("Back to Home"):
            st.session_state.page = "home"
            st.rerun()

    
    with signup_tab:
        show_signup()

def authenticate(name, password):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["influencer_marketing"]
    brand = db.brands.find_one({"username": name})
    
    if brand and check_password_hash(brand["password"], password):
        st.session_state.brand = brand
        st.session_state.page = "brand_dash"  # Updated to URL-style
        st.rerun()
    else:
        st.error("Invalid credentials")