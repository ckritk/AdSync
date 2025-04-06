import streamlit as st

# Page Config
st.set_page_config(page_title="Influencer Marketing Platform", layout="centered")

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = "home"
if 'influencer' not in st.session_state:
    st.session_state.influencer = None

# Page Navigation
def home():
    st.title("Welcome to Influencer Marketing Hub")
    st.write("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Brand Portal", use_container_width=True, key="brand_btn"):
            st.session_state.page = "brand_login"
            st.rerun()
    with col2:
        if st.button("Influencer Portal", use_container_width=True, key="influencer_btn"):
            st.session_state.page = "influencer_login"
            st.rerun()

# Router
if st.session_state.page == "home":
    home()
elif st.session_state.page == "influencer_login":
    import influ_login
    influ_login.show()
elif st.session_state.page == "influencer_dashboard":
    import influ_dash
    influ_dash.show()
elif st.session_state.page == "brand_login":
    import brand_login
    brand_login.show()
elif st.session_state.page == "brand_dash":
    # import brand_dash
    # brand_dash.show()
    # from pages import campaigns
    # campaigns.show()
    target_url = f"https://30g468db-8501.inc1.devtunnels.ms/"

    st.markdown(f"""
        <meta http-equiv="refresh" content="0; url={target_url}" />
    """, unsafe_allow_html=True)
elif st.session_state.page == "similar_influencers":
    import similar_influencers
    similar_influencers.show()
elif st.session_state.page == "schedule_post":
    import app
    app.show()