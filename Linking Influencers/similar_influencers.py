import streamlit as st
from pymongo import MongoClient
import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler

# Load pre-trained vectorizer and model
@st.cache_resource
def load_artifacts():
    topic_vectorizer = joblib.load("models/topic_vectorizer.joblib")
    metric_model = joblib.load("models/metric_model.joblib")
    fallback_df = pd.read_pickle("models/processed_data.pkl")
    return topic_vectorizer, metric_model, fallback_df

# Function to find similar influencers from MongoDB
def find_similar_influencers(db, selected_name, topic_vectorizer, metric_model, top_k=5):
    influencers = list(db.influencers.find({}))
    if not influencers:
        return pd.DataFrame()

    df = pd.DataFrame(influencers)

    # Ensure columns exist
    df.rename(columns={'name': 'NAME', 'topics': 'TOPIC OF INFLUENCE'}, inplace=True)
    for col in ['NAME', 'TOPIC OF INFLUENCE', 'FOLLOWERS', 'ER', 'POTENTIAL_REACH']:
        if col not in df.columns:
            df[col] = None

    df.dropna(subset=['NAME', 'TOPIC OF INFLUENCE'], inplace=True)

    # Convert types
    df['FOLLOWERS'] = pd.to_numeric(df['FOLLOWERS'], errors='coerce').fillna(0)
    df['POTENTIAL_REACH'] = pd.to_numeric(df['POTENTIAL_REACH'], errors='coerce').fillna(0)
    df['ER'] = pd.to_numeric(df['ER'], errors='coerce').fillna(0)

    # Format topics for vectorizer
    df['TOPIC OF INFLUENCE'] = df['TOPIC OF INFLUENCE'].apply(lambda x: ' '.join(x) if isinstance(x, list) else str(x))

    # Find selected influencer
    if selected_name not in df['NAME'].values:
        return pd.DataFrame()

    target_idx = df[df['NAME'] == selected_name].index[0]
    target_topic = df.at[target_idx, 'TOPIC OF INFLUENCE']

    # Phase 1: Topic similarity
    topic_sim = topic_vectorizer.transform([target_topic])
    all_topics = topic_vectorizer.transform(df['TOPIC OF INFLUENCE'])
    topic_scores = np.dot(all_topics, topic_sim.T).toarray().flatten()

    topic_threshold = np.quantile(topic_scores, 0.8)
    topic_mask = topic_scores >= topic_threshold
    topic_filtered = df[topic_mask].copy()

    if len(topic_filtered) <= 1:
        return pd.DataFrame()

    # Phase 2: Metric similarity
    metric_data = topic_filtered[['FOLLOWERS', 'ER', 'POTENTIAL_REACH']]
    metric_data_scaled = StandardScaler().fit_transform(metric_data)

    if target_idx in topic_filtered.index:
        target_vector = metric_data_scaled[topic_filtered.index.get_loc(target_idx)].reshape(1, -1)
    else:
        target_vector = metric_data_scaled[0].reshape(1, -1)

    distances, indices = metric_model.kneighbors(target_vector, n_neighbors=min(top_k + 1, len(topic_filtered)))

    results = topic_filtered.iloc[indices[0]].copy()
    results['Topic Similarity'] = topic_scores[results.index]
    results['Metric Distance'] = distances[0]
    results['Similarity Score'] = 100 - results['Metric Distance'] * 10  # You can tweak this

    return results.sort_values("Metric Distance")


def show():
    st.title("🔍 Find Similar Influencers")
    st.write("---")

    # Connect to MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    db = client["influencer_marketing"]

    # Load models
    topic_vectorizer, metric_model, fallback_df = load_artifacts()

    # Get names from DB
    all_influencers = list(db.influencers.find({}, {"name": 1}))
    names = [i['name'] for i in all_influencers if 'name' in i]

    if not names:
        st.error("No influencer data found.")
        return

    selected_name = st.selectbox("Select an influencer to find similar ones:", names)

    if st.button("Find Similar Influencers"):
        with st.spinner("Finding similar influencers..."):
            results = find_similar_influencers(db, selected_name, topic_vectorizer, metric_model)

        if results.empty:
            st.warning("No similar influencers found.")
        else:
            st.success(f"Found {len(results)} similar influencers for {selected_name}")
            for _, row in results.iterrows():
                with st.container(border=True):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.subheader(row["NAME"])
                        st.write(f"**Handle:** {row.get('handle', '')}")
                        st.write(f"**Followers:** {int(row.get('FOLLOWERS', 0)):,}")
                        st.write(f"**Topics:** {row['TOPIC OF INFLUENCE']}")
                        st.write(f"**Country:** {row.get('COUNTRY', '')}")
                    with col2:
                        # st.metric("Similarity", f"{row['Similarity Score']:.1f}%")
                        if st.button("Select", key=f"select_{row['_id']}"):
                            st.session_state.selected_influencer = row.to_dict()
                            st.success(f"Selected @{row.get('handle', '')}")

    if st.button("← Back to Dashboard"):
        st.session_state.page = "brand_dash"
        st.rerun()
