import os
import pandas as pd
import numpy as np
import faiss
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt

class KNNEngine:
    def __init__(self, feature_dim):
        self.feature_dim = feature_dim
        self.index = faiss.IndexFlatL2(self.feature_dim)  # Use L2 (Euclidean) distance

    def build_index(self, features):
        features = np.ascontiguousarray(features, dtype=np.float32)  # FAISS expects float32 arrays
        self.index.add(features)

    def query(self, query_vector, k=5):
        query_vector = np.ascontiguousarray(query_vector.reshape(1, -1), dtype=np.float32)
        distances, indices = self.index.search(query_vector, k)
        return indices[0], distances[0]

class DimensionalityReducer:
    def __init__(self, features):
        self.features = features

    def apply_tsne(self):
        tsne = TSNE(n_components=2, perplexity=30, n_iter=1000, random_state=42)
        reduced_features = tsne.fit_transform(self.features)
        return reduced_features

def load_descriptors(csv_filepath):
    """
    Loads the CSV file containing object descriptors, 
    and returns a DataFrame and the features (without name and class).
    """
    # Check if file exists before loading
    if os.path.exists(csv_filepath):
        print("File found! Loading...")
        df = pd.read_csv(csv_filepath)
        features = df.drop(columns=['name', 'class']).values  # Drop 'name' and 'class' for feature matrix
        return df, features
    else:
        print(f"File not found at: {csv_filepath}")
        return None, None

def visualize_tsne_2d(reduced_features, labels, title="t-SNE Visualization"):
    """
    Creates a 2D scatterplot of the t-SNE results, coloring by class labels.
    """
    plt.figure(figsize=(10, 7))
    unique_labels = np.unique(labels)
    
    for label in unique_labels:
        indices = np.where(labels == label)
        plt.scatter(reduced_features[indices, 0], reduced_features[indices, 1], label=label, s=50)
    
    plt.title(title)
    plt.xlabel('Component 1')
    plt.ylabel('Component 2')
    plt.legend()
    plt.show()

def select_shape_by_name(df):
    """
    Allows the user to select a shape by name from the DataFrame.
    :param df: pandas DataFrame containing shape descriptors
    :return: The index of the selected shape in the DataFrame
    """
    print("Available shapes:")
    for index, row in df.iterrows():
        print(f"- {row['name']}")

    shape_name = input("Enter the name of the shape to query: ")
    if shape_name in df['name'].values:
        return df[df['name'] == shape_name].index[0]
    else:
        print("Shape not found!")
        return None

def main():
    # Full path to your CSV file
    csv_filepath = r'C:\Universiteit\HCI\MultimediaRetrieval\steps\step5\objDescriptors.csv'  # Change this to your actual path

    # Load shape descriptors from CSV
    df, features = load_descriptors(csv_filepath)

    # If file not found or failed to load
    if df is None or features is None:
        print("Failed to load descriptors. Exiting.")
        return

    # K-Nearest Neighbors (KNN) search using FAISS
    knn = KNNEngine(feature_dim=features.shape[1])  # Number of features in the CSV
    knn.build_index(features)

    # Allow the user to select a shape by name
    selected_shape_idx = select_shape_by_name(df)
    if selected_shape_idx is None:
        return  # Exit if the shape was not found

    # Use the selected shape's feature vector as the query
    query_vector = features[selected_shape_idx]  # Get feature vector of the selected shape
    k = 5  # Number of neighbors to find
    neighbors, distances = knn.query(query_vector, k=k)
    
    # Print results
    print(f"Query shape: {df.iloc[selected_shape_idx]['name']}")
    print("K-Nearest Neighbors:")
    for i, neighbor_idx in enumerate(neighbors):
        shape_name = df.iloc[neighbor_idx]['name']
        print(f"{i + 1}: Shape = {shape_name}, Distance = {distances[i]}")

    # Dimensionality Reduction (t-SNE)
    dr = DimensionalityReducer(features)
    reduced_features = dr.apply_tsne()

    # Visualize the t-SNE scatterplot, color by 'class'
    labels = df['class'].values
    visualize_tsne_2d(reduced_features, labels)

def test_input():
    print("Available shapes:")
    shapes = ["Cube", "Sphere", "Cylinder"]  # Example shapes
    for shape in shapes:
        print(f"- {shape}")

    shape_name = input("Enter the name of the shape to query: ")
    if shape_name in shapes:
        print(f"You selected: {shape_name}")
    else:
        print("Shape not found!")

if __name__ == "__main__":
    #main()
    test_input()
