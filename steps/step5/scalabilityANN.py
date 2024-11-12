import os
import pandas as pd
import numpy as np
import faiss
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import matplotlib.cm as cm

class KNNEngine:
    def __init__(self, feature_dim, nlist=100, nprobe=10):
        self.feature_dim = feature_dim
        self.nlist = nlist  # Number of clusters
        self.nprobe = nprobe  # Number of clusters to search within

        # Initialize a quantizer for clustering
        self.quantizer = faiss.IndexFlatL2(feature_dim)  
        # Create an IVF index for approximate search
        self.index = faiss.IndexIVFFlat(self.quantizer, feature_dim, nlist)
        self.index.nprobe = nprobe  # Set the number of clusters to search

    def build_index(self, features):
        features = np.ascontiguousarray(features, dtype=np.float32)
        # Train the index for clustering (necessary for IVF)
        self.index.train(features)
        # Add features to the index
        self.index.add(features)

    def query(self, query_vector, k=5):
        query_vector = np.ascontiguousarray(query_vector.reshape(1, -1), dtype=np.float32)
        # Perform the ANN search
        distances, indices = self.index.search(query_vector, k + 1)
        # Exclude the query itself from results
        indices, distances = indices[0][1:k+1], distances[0][1:k+1]
        return indices, distances

class DimensionalityReducer:
    def __init__(self, features):
        self.features = features

    def apply_tsne(self):
        tsne = TSNE(n_components=2, perplexity=30, n_iter=1000, random_state=42)
        reduced_features = tsne.fit_transform(self.features)
        return reduced_features

def parse_descriptor_columns(df):
    for col in ['A3', 'D1', 'D2', 'D3', 'D4']:
        df[col] = df[col].apply(lambda x: np.fromstring(x, sep=','))

    feature_matrix = np.hstack([
        df['surfaceAreaObj'].values.reshape(-1, 1),
        df['compactnessObj'].values.reshape(-1, 1),
        df['rectangularityObj'].values.reshape(-1, 1),
        df['diameterObj'].values.reshape(-1, 1),
        df['convexityObj'].values.reshape(-1, 1),
        df['eccentricityObj'].values.reshape(-1, 1),
        np.vstack(df['A3'].values),
        np.vstack(df['D1'].values),
        np.vstack(df['D2'].values),
        np.vstack(df['D3'].values),
        np.vstack(df['D4'].values)
    ])
    return feature_matrix

def load_descriptors(csv_filepath):
    if os.path.exists(csv_filepath):
        print("File found! Loading...")
        df = pd.read_csv(csv_filepath)
        feature_matrix = parse_descriptor_columns(df)
        return df, feature_matrix
    else:
        print(f"File not found at: {csv_filepath}")
        return None, None

def visualize_tsne_2d(reduced_features, labels, highlight_index=None, title="t-SNE Visualization"):
    plt.figure(figsize=(12, 8))
    
    unique_labels = np.unique(labels)
    colors = cm.get_cmap("tab20", len(unique_labels))  # Use 'tab20' for up to 20 distinct colors

    for idx, label in enumerate(unique_labels):
        indices = np.where(labels == label)
        plt.scatter(reduced_features[indices, 0], reduced_features[indices, 1], 
                    label=label, color=colors(idx), s=50, alpha=0.7)

    if highlight_index is not None:
        plt.scatter(reduced_features[highlight_index, 0], reduced_features[highlight_index, 1], 
                    color='red', s=100, edgecolor='black', label='Selected Shape', zorder=5)

    plt.title(title, fontsize=16)
    plt.xlabel('Component 1', fontsize=12)
    plt.ylabel('Component 2', fontsize=12)
    plt.legend(title="Class", bbox_to_anchor=(1.05, 1), loc='upper left', 
               borderaxespad=0., fontsize='small', ncol=2)
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def select_shape_by_name(df):
    print("Available shapes:")
    for index, row in df.iterrows():
        print(f"- {row['name']}")

    shape_name = input("Enter the name of the shape to query: ")
    selected_shape_idx = df[df['name'].str.lower() == shape_name.lower()].index
    if len(selected_shape_idx) == 0:
        print("Shape not found!")
        return None
    return selected_shape_idx[0]

def main():
    csv_filepath = r'C:\Universiteit\MultimediaRetrieval\steps\AxelHoekje\dataBaseFinal.csv'

    df, features = load_descriptors(csv_filepath)
    if df is None or features is None:
        print("Failed to load descriptors. Exiting.")
        return

    # Initialize KNN engine with ANN using IVF indexing
    knn = KNNEngine(feature_dim=features.shape[1], nlist=100, nprobe=10)
    knn.build_index(features)

    selected_shape_idx = select_shape_by_name(df)
    if selected_shape_idx is None:
        return

    query_vector = features[selected_shape_idx]
    k = 5
    neighbors, distances = knn.query(query_vector, k=k)

    print(f"Query shape: {df.iloc[selected_shape_idx]['name']}")
    print("K-Nearest Neighbors:")
    for i, neighbor_idx in enumerate(neighbors):
        shape_name = df.iloc[neighbor_idx]['name']
        shape_class = df.iloc[neighbor_idx]['class']
        print(f"{i + 1}: Shape = {shape_name}, Class = {shape_class}, Distance = {distances[i]}")

    dr = DimensionalityReducer(features)
    reduced_features = dr.apply_tsne()

    labels = df['class'].values
    visualize_tsne_2d(reduced_features, labels, highlight_index=selected_shape_idx)

if __name__ == "__main__":
    main()
