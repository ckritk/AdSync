import streamlit as st
from pymongo import MongoClient
from datetime import datetime

def show():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["influencer_marketing"]
    
    st.title(f"👔 {st.session_state.brand['username']} Dashboard")
    st.write("---")

    if st.button("🔍 Find Similar Influencers", use_container_width=True):
        st.session_state.page = "similar_influencers"
        st.rerun()

    # Tab system
    tab1, tab2 = st.tabs(["Find Influencers", "Your Campaigns"])
    
    with tab1:
        show_influencer_finder(db)
    
    with tab2:
        show_campaigns(db)

def show_influencer_finder(db):
    """Show influencer search and filtering"""
    st.header("Find Influencers")
    
    with st.form("filter_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            topic = st.text_input("Topic (e.g., Fashion)")
            min_rate = st.number_input("Minimum Rate ($)", min_value=0, value=500)
            country = st.text_input("Country")
            
        with col2:
            min_followers = st.number_input("Min Followers (millions)", min_value=0, value=1)
            platform = st.selectbox("Platform", ["Any", "Instagram", "YouTube", "TikTok"])
            min_reach = st.number_input("Min Potential Reach (millions)", min_value=0, value=1)
        
        submitted = st.form_submit_button("Search")
    
    if submitted:
        print("CALLED")
        search_influencers(db, topic, min_rate, country, min_followers, platform, min_reach)

def search_influencers(db, topic, min_rate, country, min_followers, platform, min_reach):
    """Query influencers based on filters"""
    query = {
        "MIN_PRICE": {"$lte": min_rate},
        "FOLLOWERS": {"$gte": min_followers * 1_000_000},
        "POTENTIAL_REACH": {"$gte": min_reach * 1_000_000}
    }
    
    if topic:
        query["topics"] = {"$regex": topic, "$options": "i"}
    if country:
        query["COUNTRY"] = {"$regex": country, "$options": "i"}
    if platform != "Any":
        query["Platform"] = platform
        
    influencers = db.influencers.find(query).sort({ "FOLLOWERS": -1 }).limit(50)


    if not influencers:
        st.warning("No influencers match your criteria")
        return
    
    for influencer in influencers:
        print(influencer)
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.subheader(influencer["name"])
                st.write(f"**Handle:** {influencer['handle']}")
                st.write(f"**Country:** {influencer['COUNTRY']}")
                st.write(f"**Followers:** {influencer.get('FOLLOWERS', 0):,}")
                st.write(f"**Potential Reach:** {influencer.get('POTENTIAL_REACH', 0):,}")
                st.write(f"**Rate:** ${influencer.get('MIN_PRICE', 0)}")
                st.write(f"**Platform:** {influencer['Platform']}")
                st.write(f"**Topics:** {', '.join(influencer.get('topics', []))}")
            
            with col2:
                if st.button("Request", key=f"req_{influencer['_id']}"):
                    st.session_state.request_influencer = influencer
                    st.session_state.show_request_form = True
            
            if st.session_state.get("show_request_form") and st.session_state.request_influencer["_id"] == influencer["_id"]:
                with st.form(key=f"request_form_{influencer['_id']}"):
                    product = st.text_input("Product Name")
                    details = st.text_area("Campaign Details")
                    offer = st.number_input("Your Offer ($)", min_value=influencer.get("MIN_PRICE", 0))
                    
                    if st.form_submit_button("Send Request"):
                        pass
                        #soka inga


def show_campaigns(db):
    """Show brand's existing campaigns"""
    st.header("Your Campaigns")
    
    campaign_list = db.campaigns.find({"brand": st.session_state.brand["username"]}).sort("created_at", -1)
    
    if campaign_list == None:
        st.info("You haven't created any campaigns yet")
        return
    
    for campaign in campaign_list:
        status_color = {
            "requested": "blue",
            "approved": "green",
            "rejected": "red",
            "completed": "gray"
        }.get(campaign["status"], "gray")
        
        with st.container(border=True):
            st.markdown(f"**Product:** {campaign['product']}")
            st.markdown(f"**Influencer:** {campaign['influencer']}")
            st.markdown(f"**Rate:** ${campaign['rate']}")
            st.markdown(f"**Status:** :{status_color}[{campaign['status'].upper()}]")
            st.markdown(f"**Details:** {campaign.get('details', '')}")
            st.caption(f"Created on: {campaign['created_at'].strftime('%Y-%m-%d')}")

def logout():
    st.session_state.brand = None
    st.session_state.page = "home"
    st.rerun()

# Add logout button at bottom
st.write("---")
if st.button("Logout"):
    logout()