
from pymongo import MongoClient
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler, MultiLabelBinarizer
import numpy as np
import pandas as pd
from bson import ObjectId

class InfluencerMatcher:
    def __init__(self, k=5):
        self.k = k
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["clicktracker"]
        self.collection = self.db["influencers"]
        self._prepare_data()

    def _prepare_data(self):
        docs = list(self.collection.find())
        self.df = pd.DataFrame(docs)

        if "_id" not in self.df.columns:
            raise ValueError("Expected '_id' in influencer documents.")

        self.influencer_ids = self.df["_id"].tolist()

        # Select numeric and categorical features for similarity
        numeric_features = ["FOLLOWERS", "ER"]
        categorical_features = ["topics", "COUNTRY", "Platform"]

        # Fill missing numeric with 0
        self.df[numeric_features] = self.df[numeric_features].fillna(0)

        # Convert to float
        for col in numeric_features:
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce').fillna(0)

        # Scale numeric
        scaler = StandardScaler()
        scaled_numeric = scaler.fit_transform(self.df[numeric_features])

        # One-hot encode categorical (including multi-label topics)
        mlb = MultiLabelBinarizer()
        topics_encoded = mlb.fit_transform(self.df["topics"].apply(lambda x: x if isinstance(x, list) else []))

        country_encoded = pd.get_dummies(self.df["COUNTRY"].fillna("Unknown"))
        platform_encoded = pd.get_dummies(self.df["Platform"].fillna("Unknown"))

        # Combine all features
        self.feature_matrix = np.hstack([scaled_numeric, topics_encoded, country_encoded.values, platform_encoded.values])

        # Fit Nearest Neighbors model
        self.nn_model = NearestNeighbors(n_neighbors=self.k + 1, metric="euclidean")  # +1 to skip the influencer itself
        self.nn_model.fit(self.feature_matrix)

    def find_similar(self, selected_id):
        if selected_id not in self.influencer_ids:
            return []

        idx = self.influencer_ids.index(selected_id)
        query_vector = self.feature_matrix[idx].reshape(1, -1)

        distances, indices = self.nn_model.kneighbors(query_vector)

        similar_indices = [i for i in indices[0] if i != idx][:self.k]
        return self.df.iloc[similar_indices].to_dict(orient="records")
