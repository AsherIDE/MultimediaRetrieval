import os
import pandas as pd
import numpy as np
import faiss

# Same as part 5
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

# Load descriptors with parsed columns
def load_descriptors(csv_filepath):
    if os.path.exists(csv_filepath):
        print("File found! Loading...")
        df = pd.read_csv(csv_filepath)
        feature_matrix = parse_descriptor_columns(df)
        return df, feature_matrix
    else:
        print(f"File not found at: {csv_filepath}")
        return None, None

# FAISS-based ANN Engine for Evaluation
class ANNEvaluationEngine:
    def __init__(self, feature_dim, nlist=100):
        self.feature_dim = feature_dim
        self.nlist = nlist  # Number of clusters for the inverted index
        self.index = faiss.IndexIVFFlat(faiss.IndexFlatL2(feature_dim), feature_dim, nlist)
        self.index.nprobe = 10  # Number of clusters to search (controls accuracy/speed)

    def train_index(self, features):
        features = np.ascontiguousarray(features, dtype=np.float32)  # Ensure correct format
        print("Training the FAISS index with clustering for ANN...")
        self.index.train(features)  # Train on the feature set
        self.index.add(features)  # Add features to the trained FAISS index

    def query(self, query_vector, k=7):
        query_vector = np.ascontiguousarray(query_vector.reshape(1, -1), dtype=np.float32)
        distances, indices = self.index.search(query_vector, k + 1)  # Search for k+1 neighbors to exclude self
        indices, distances = indices[0][1:k+1], distances[0][1:k+1]  # Exclude the query shape itself
        return indices, distances

# Calculate precision and recall
def calculate_precision_recall(df, knn_engine, feature_matrix, k=7):
    correct_matches = 0
    total_relevant = 0
    total_retrieved = 0
    precision_per_class = {}
    recall_per_class = {}

    for idx, query_shape in df.iterrows():
        query_vector = feature_matrix[idx]
        query_class = query_shape['class']
        
        # Retrieve k-nearest neighbors using FAISS
        neighbors, _ = knn_engine.query(query_vector, k=k)

        # Calculate true positives
        relevant_retrieved = sum(1 for neighbor_idx in neighbors if df.iloc[neighbor_idx]['class'] == query_class)
        total_relevant += sum(1 for _ in df[df['class'] == query_class].index)
        correct_matches += relevant_retrieved
        total_retrieved += k

        # Precision and Recall per class
        if query_class not in precision_per_class:
            precision_per_class[query_class] = []
            recall_per_class[query_class] = []
        
        precision = relevant_retrieved / k if k > 0 else 0
        recall = relevant_retrieved / total_relevant if total_relevant > 0 else 0

        precision_per_class[query_class].append(precision)
        recall_per_class[query_class].append(recall)

    # Calculate aggregate precision and recall for each class
    avg_precision_per_class = {cls: np.mean(precisions) for cls, precisions in precision_per_class.items()}
    avg_recall_per_class = {cls: np.mean(recalls) for cls, recalls in recall_per_class.items()}

    # Grand aggregate (overall precision and recall)
    overall_precision = correct_matches / total_retrieved if total_retrieved > 0 else 0
    overall_recall = correct_matches / total_relevant if total_relevant > 0 else 0

    return avg_precision_per_class, avg_recall_per_class, overall_precision, overall_recall

def main():
    csv_filepath = r'C:\Universiteit\MultimediaRetrieval\steps\AxelHoekje\dataBaseFinal.csv'

    # Load the descriptors
    df, feature_matrix = load_descriptors(csv_filepath)
    if df is None or feature_matrix is None:
        print("Failed to load descriptors. Exiting.")
        return

    # Initialize and train the FAISS ANN index
    ann_engine = ANNEvaluationEngine(feature_dim=feature_matrix.shape[1])
    ann_engine.train_index(feature_matrix)

    # Set K for ANN
    k = 7

    # Calculate precision and recall
    avg_precision_per_class, avg_recall_per_class, overall_precision, overall_recall = calculate_precision_recall(df, ann_engine, feature_matrix, k=k)

    # Display results
    print("Average Precision per Class:")
    for cls, precision in avg_precision_per_class.items():
        print(f"Class {cls}: Precision = {precision:.2f}")
    
    print("\nAverage Recall per Class:")
    for cls, recall in avg_recall_per_class.items():
        print(f"Class {cls}: Recall = {recall:.2f}")
    
    print(f"\nOverall Precision: {overall_precision:.2f}")
    print(f"Overall Recall: {overall_recall:.2f}")

if __name__ == "__main__":
    main()  
