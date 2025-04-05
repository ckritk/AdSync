import streamlit as st
import requests

# Redirect if not logged in
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("Please log in first.")
    st.stop()

user_id = st.session_state['user_id']
username = st.session_state['username']
st.title(f"{username}'s Campaigns")

# Fetch campaigns
try:
    response = requests.get(f"http://localhost:3000/user/{user_id}/campaigns")
    if response.status_code == 200:
        campaigns = response.json().get('campaigns', [])

        if not campaigns:
            st.info("No campaigns found.")
        else:
            st.subheader("Your Campaigns")
            for campaign in campaigns:
                if st.button(campaign['name'], key=f"campaign_button_{campaign['_id']}"):
                    st.session_state['selected_campaign_id'] = campaign['_id']
                    st.session_state['selected_campaign_name'] = campaign['name']
                    st.switch_page("pages/campaign_details.py")

    else:
        st.error("Failed to load campaigns.")
except Exception as e:
    st.error("Error fetching campaigns.")
    st.text(str(e))

# Divider
st.markdown("---")
st.subheader("Add New Campaign")

new_campaign_name = st.text_input("Campaign Name")

if st.button("Create Campaign"):
    if new_campaign_name.strip() == "":
        st.warning("Campaign name cannot be empty.")
    else:
        try:
            res = requests.post(
                "http://localhost:3000/campaign/create",
                json={"name": new_campaign_name, "userId": user_id}
            )

            if res.status_code == 200:
                st.success("Campaign created successfully!")
                st.rerun()
            else:
                st.error("Failed to create campaign.")
        except Exception as e:
            st.error("Error connecting to backend.")
            st.text(str(e))
