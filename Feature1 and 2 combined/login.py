import streamlit as st
import requests

st.title("Login")

# If already logged in, redirect to campaigns
if st.session_state.get("logged_in"):
    st.switch_page("pages/campaigns.py")

username = st.text_input("Enter your username")

if st.button("Login"):
    if username.strip() == "":
        st.warning("Username cannot be empty.")
    else:
        try:
            response = requests.post("http://localhost:3000/user/login", json={"username": username})

            if response.status_code == 200:
                data = response.json()

                # Save to session state
                st.session_state['user_id'] = data['userId']
                st.session_state['username'] = data['username']
                st.session_state['logged_in'] = True

                # Redirect to campaigns page
                st.switch_page("pages/campaigns.py")

            else:
                st.error(f"Login failed: {response.text}")
        except Exception as e:
            st.error("Could not connect to backend.")
            st.text(str(e))
