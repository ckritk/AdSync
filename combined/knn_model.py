# knn_model.py

from pymongo import MongoClient
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler, MultiLabelBinarizer
import numpy as np
import pandas as pd

class InfluencerMatcher:
    def __init__(self, k=5):
        self.k = k
        self.model = None
        self.df = None
        self.feature_matrix = None
        self.influencer_ids = []
        self.mlb = MultiLabelBinarizer()
        self.scaler = StandardScaler()
        self._prepare_data()

    def _prepare_data(self):
        client = MongoClient("mongodb://localhost:27017/")
        db = client["influencer_marketing"]
        collection = db["influencers"]
        influencers = list(collection.find({}))

        self.df = pd.DataFrame(influencers)
        self.influencer_ids = self.df["_id"].tolist()

        # Fix null topics: convert anything that's not a list to empty list
        self.df["topics"] = self.df["topics"].apply(lambda x: x if isinstance(x, list) else [])

        # Fill missing numeric values
        self.df.fillna({"FOLLOWERS": 0, "ER": 0, "POTENTIAL_REACH": 0}, inplace=True)

        # Encode topics
        topic_features = self.mlb.fit_transform(self.df["topics"])

        # Scale numerical features
        num_features = self.df[["FOLLOWERS", "ER", "POTENTIAL_REACH"]]
        scaled_num = self.scaler.fit_transform(num_features)

        # Combine all features
        self.feature_matrix = np.hstack((scaled_num, topic_features))

        self.model = NearestNeighbors(n_neighbors=self.k + 1, metric='cosine')
        self.model.fit(self.feature_matrix)


    def find_similar(self, influencer_id):
        if influencer_id not in self.influencer_ids:
            return []

        idx = self.influencer_ids.index(influencer_id)
        input_vector = self.feature_matrix[idx].reshape(1, -1)

        distances, indices = self.model.kneighbors(input_vector)

        similar_indices = indices.flatten()[1:]  # Skip self
        return self.df.iloc[similar_indices][["handle", "name", "FOLLOWERS", "ER", "topics", "COUNTRY", "Platform"]].to_dict(orient="records")
