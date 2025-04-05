import streamlit as st
import requests
import pandas as pd
import plotly.express as px

from pymongo import MongoClient
from datetime import datetime


# Ensure user is logged in
if not st.session_state.get("logged_in"):
    st.switch_page("login.py")

if 'selected_campaign_id' not in st.session_state:
    st.warning("No campaign selected.")
    st.stop()

campaign_id = st.session_state['selected_campaign_id']
campaign_name = st.session_state['selected_campaign_name']
st.title(f"Campaign: {campaign_name}")

BASE_URL = "http://localhost:3000"

# ---- FETCH CAMPAIGN DETAILS ----
def fetch_campaign():
    try:
        res = requests.get(f"{BASE_URL}/campaign/{campaign_id}")
        if res.status_code == 200:
            return res.json().get("campaign")
        else:
            st.error("Failed to fetch campaign details.")
    except Exception as e:
        st.error("Could not connect to backend.")
        st.text(str(e))
    return {}

campaign = fetch_campaign()

# ---- STATS SECTION ----
def get_click_data(urls):
    return [(url['name'], url.get('clicks', 0)) for url in urls]

campaign_clicks = get_click_data(campaign.get("campaignUrls", []))
conversion_clicks = get_click_data(campaign.get("conversionUrls", []))

total_campaign_clicks = sum(c[1] for c in campaign_clicks)
total_conversion_clicks = sum(c[1] for c in conversion_clicks)
total_clicks = total_campaign_clicks + total_conversion_clicks

conversion_rate = (total_conversion_clicks / total_campaign_clicks * 100) if total_campaign_clicks else 0

# Show totals and conversion rate
st.markdown("### Overview Stats")
col1, col2, col3 = st.columns(3)
col1.metric("Total Clicks", total_clicks)
col2.metric("Campaign Clicks", total_campaign_clicks)
col3.metric("Conversion Rate", f"{conversion_rate:.2f}%")

# Show bar chart of campaign clicks
if campaign_clicks:
    st.markdown("### Campaign URL Clicks")
    col_bar, _ = st.columns([2, 1])
    df_bar = pd.DataFrame(campaign_clicks, columns=["URL", "Clicks"])
    fig = px.bar(df_bar, x="URL", y="Clicks", color="URL", text="Clicks", height=300)
    col_bar.plotly_chart(fig, use_container_width=True)

# ---- ADVANCED LOGS ANALYTICS ----
def extract_logs(urls):
    logs = []
    for url in urls:
        for log in url.get('logs', []):
            log['urlName'] = url.get('name')
            logs.append(log)
    return logs

logs = extract_logs(campaign.get("campaignUrls", []) + campaign.get("conversionUrls", []))
if logs:
    df_logs = pd.DataFrame(logs)
    df_logs['timestamp'] = pd.to_datetime(df_logs['timestamp'])

    st.markdown("### Click Trends")

    # Layout for main charts
    col1, col2 = st.columns(2)

    with col1:
        st.caption("Clicks Over Time")
        clicks_time = df_logs.groupby(df_logs['timestamp'].dt.date).size().reset_index(name='Clicks')
        fig_time = px.line(clicks_time, x='timestamp', y='Clicks', markers=True, height=250)
        st.plotly_chart(fig_time, use_container_width=True)

    with col2:
        st.caption("Location Distribution")
        location_dist = df_logs['location'].fillna("Unknown").value_counts().reset_index()
        location_dist.columns = ['Location', 'Clicks']
        fig_loc = px.bar(location_dist, x='Location', y='Clicks', text='Clicks', height=250)
        st.plotly_chart(fig_loc, use_container_width=True)

    # Grouped expanders for less important charts
    with st.expander("Referrer Domains"):
        df_logs['referrerDomain'] = df_logs['referrer'].fillna("Unknown").apply(
            lambda x: x.split('/')[2] if '//' in x else x
        )
        top_referrers = df_logs['referrerDomain'].value_counts().reset_index()
        top_referrers.columns = ['Referrer', 'Clicks']
        fig_ref = px.bar(top_referrers, x='Referrer', y='Clicks', text='Clicks', height=250)
        st.plotly_chart(fig_ref, use_container_width=True)

    with st.expander("Device/Browser Usage"):
        col1, col2 = st.columns(2)
        with col1:
            device_counts = df_logs['deviceType'].fillna("Unknown").value_counts().reset_index()
            device_counts.columns = ['Device', 'Clicks']
            fig_device = px.bar(device_counts, x='Device', y='Clicks', text='Clicks', color='Device', height=250)
            st.plotly_chart(fig_device, use_container_width=True)
        with col2:
            browser_counts = df_logs['browser'].fillna("Unknown").value_counts().reset_index()
            browser_counts.columns = ['Browser', 'Clicks']
            fig_browser = px.bar(browser_counts, x='Browser', y='Clicks', text='Clicks', color='Browser', height=250)
            st.plotly_chart(fig_browser, use_container_width=True)

# ---- DISPLAY SECTION ----
if campaign:
    st.subheader("Influencers")
    influencers = campaign.get("influencers", [])

    if influencers:
        for inf_obj in influencers:
            inf = inf_obj.get("influencer", {})
            status = inf_obj.get("status", "unknown").capitalize()
            name = inf.get("name", "Unnamed")
            st.markdown(
                f"""
                <div style='padding: 10px; border: 1px solid #DDD; border-radius: 6px; margin-bottom: 8px;'>
                    <strong>{name}</strong>
                    <span style='float: right; color: #666;'>Status: <em>{status}</em></span>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.info("No influencers linked yet.")

    st.subheader("Campaign URLs")
    if campaign.get("campaignUrls"):
        for url in campaign.get("campaignUrls", []):
            with st.container():
                col1, col2 = st.columns([0.85, 0.15])
                with col1:
                    st.markdown(
                        f"""
                        <div style='padding: 10px; border: 1px solid #DDD; border-radius: 6px; margin-bottom: 6px;'>
                            <div style='display: flex; gap: 10px; align-items: center;'>
                                <strong>{url['name']}</strong>
                                <a href="http://localhost:3000/{url['shortId']}" target="_blank" style="font-size: 13px; text-decoration: none; color: #1a73e8;">🔗 link</a>
                            </div>
                            <code style='font-size: 12px; color: #888;'>{url['shortId']}</code>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with col2:
                    if st.button("Stats", key=f"campaign_stats_{url['_id']}"):
                        st.session_state['selected_url_id'] = url['_id']
                        st.session_state['selected_url_name'] = url['name']
                        st.switch_page("pages/url_stats.py")
    else:
        st.info("No campaign URLs added.")

    st.subheader("Conversion URLs")
    if campaign.get("conversionUrls"):
        for url in campaign.get("conversionUrls", []):
            with st.container():
                col1, col2 = st.columns([0.85, 0.15])
                with col1:
                    st.markdown(
                        f"""
                        <div style='padding: 10px; border: 1px solid #DDD; border-radius: 6px; margin-bottom: 6px;'>
                            <div style='display: flex; gap: 10px; align-items: center;'>
                                <strong>{url['name']}</strong>
                                <a href="http://localhost:3000/{url['shortId']}" target="_blank" style="font-size: 13px; text-decoration: none; color: #e67300;">🔗 link</a>
                            </div>
                            <code style='font-size: 12px; color: #888;'>{url['shortId']}</code>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with col2:
                    if st.button("Stats", key=f"conversion_stats_{url['_id']}"):
                        st.session_state['selected_url_id'] = url['_id']
                        st.session_state['selected_url_name'] = url['name']
                        st.switch_page("pages/url_stats.py")
    else:
        st.info("No conversion URLs added.")

# ---- ADD NEW ELEMENTS ----
st.divider()
st.subheader("Add to Campaign")

# Add Campaign URL
with st.expander("Add Campaign URL"):
    url_name = st.text_input("URL Name", key="camp_url_name")
    url_original = st.text_input("Original URL", key="camp_url_orig")
    if st.button("Add Campaign URL"):
        if url_name and url_original:
            try:
                res = requests.post(f"{BASE_URL}/campaign/addurl", json={
                    "name": url_name,
                    "originalUrl": url_original,
                    "campaignId": campaign_id,
                    "type": "campaign"
                })
                if res.status_code == 200:
                    st.success("Campaign URL added.")
                    st.rerun()
                else:
                    st.error("Failed to add URL.")
            except Exception as e:
                st.error("Error connecting to backend.")
                st.text(str(e))

# Add Conversion URL
with st.expander("Add Conversion URL"):
    conv_name = st.text_input("Conversion URL Name", key="conv_url_name")
    conv_original = st.text_input("Original URL", key="conv_url_orig")
    if st.button("Add Conversion URL"):
        if conv_name and conv_original:
            try:
                res = requests.post(f"{BASE_URL}/campaign/addurl", json={
                    "name": conv_name,
                    "originalUrl": conv_original,
                    "campaignId": campaign_id,
                    "type": "conversion"
                })
                if res.status_code == 200:
                    st.success("Conversion URL added.")
                    st.rerun()
                else:
                    st.error("Failed to add URL.")
            except Exception as e:
                st.error("Error connecting to backend.")
                st.text(str(e))

# ---- FIND INFLUENCERS ---- 
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
                    payload = {
                        "campaignId": campaign_id,
                        "influencerId": str(influencer["_id"])
                    }

                    try:
                        response = requests.post("http://localhost:3000/campaign/add-influencer", json=payload)
                        if response.status_code == 200:
                            st.success("Influencer added to campaign with status 'pending'.")
                        else:
                            st.error(f"Error: {response.json().get('error', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"Request failed: {e}")
            

client = MongoClient("mongodb://localhost:27017/")
db = client["clicktracker"]

show_influencer_finder(db)