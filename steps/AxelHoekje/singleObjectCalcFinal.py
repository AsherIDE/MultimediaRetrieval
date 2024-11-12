import numpy as np
import random
import csv
import os
from scipy.spatial import ConvexHull
from math import pi
import pandas as pd
import multiprocessing

class ObjectCalculations:
    def __init__(self, obj_file):
        self.obj_file = obj_file
        self.vertices, self.faces, self.SurfaceArea, self.volume, self.barycenter = self.load_obj(obj_file)
        self.convex_hull_volume = self.calculate_convex_hull_volume()
        self.eigenvalues = self.calculate_eigenvalues()
        self.obb_volume = self.calculate_obb_volume()
        self.surfaceAreaObj = self.calcSurfaceArea()
        self.compactnessObj = self.calcCompactness()
        self.rectangularityObj = self.rectangularity()
        self.diameterObj = self.diameter()
        self.convexityObj = self.convexity()
        self.eccentricityObj = self.eccentricity()
        self.A3, self.D1, self.D2, self.D3, self.D4 = self.compute_all_histograms()
        self.single_val_features = ["surfaceAreaObj","compactnessObj","rectangularityObj","diameterObj","convexityObj","eccentricityObj"]
        self.hist_features = ["A3","D1","D2","D3","D4"]
        

    def get_descriptors(self):
        descriptors = {
            "convex_hull_volume": self.convex_hull_volume,
            "eigenvalues": self.eigenvalues,
            "obb_volume": self.obb_volume,
            "surfaceAreaObj": self.surfaceAreaObj,
            "compactnessObj": self.compactnessObj,
            "rectangularityObj": self.rectangularityObj,
            "diameterObj": self.diameterObj,
            "convexityObj": self.convexityObj,
            "eccentricityObj": self.eccentricityObj,
            "A3": self.A3,
            "D1": self.D1,
            "D2": self.D2,
            "D3": self.D3,
            "D4": self.D4
        }
        return descriptors

    def normalizeFeatures(self):
        # get features of preprocessed search object
        self.features = self.get_descriptors()
        
        del self.features['convex_hull_volume']
        del self.features['eigenvalues']
        del self.features['obb_volume']

        # load values to standardize with
        df_features_means_stds = pd.read_csv("MultimediaRetrieval\steps\AxelHoekje\searchStandardizationData.csv")

        # standardize single-value features (hist features already done)
        for single_val_feature in self.single_val_features:
            mean = df_features_means_stds.at[0, single_val_feature]
            std = df_features_means_stds.at[1, single_val_feature]

            # update the value itself
            self.features[single_val_feature] = abs((self.features[single_val_feature] - mean) / std)
        self.surfaceAreaObj = self.features["surfaceAreaObj"]
        self.compactnessObj = self.features["compactnessObj"]
        self.rectangularityObj = self.features["rectangularityObj"]
        self.diameterObj = self.features["diameterObj"]
        self.convexityObj = self.features["convexityObj"]
        self.eccentricityObj = self.features["eccentricityObj"]
        self.A3 = self.features["A3"]
        self.D1 = self.features["D1"]
        self.D2 = self.features["D2"]
        self.D3 = self.features["D3"]
        self.D4 = self.features["D4"]
        print(self.features)

        print(f"[Finished] features: search object feature extraction and normalization complete")
        
    


    def getAllDescriptors(self):
        return self.surfaceAreaObj,self.compactnessObj,self.rectangularityObj,self.diameterObj, self.convexityObj,self.eccentricityObj, self.A3, self.D1, self.D2, self.D3, self.D4    
    def getGlobalDescriptors(self):
        return self.A3, self.D1, self.D2, self.D3, self.D4

    def write_to_csv(self):
        # Summarize the lists by taking their mean
        last_part = os.path.basename(self.obj_file)
    
        # Get the part before the last part (directory name)
        second_to_last_part = os.path.basename(os.path.dirname(self.obj_file))
        # Convert histogram data to string to avoid issues with CSV formatting
        A3_str = ','.join(map(str, self.A3))
        D1_str = ','.join(map(str, self.D1))
        D2_str = ','.join(map(str, self.D2))
        D3_str = ','.join(map(str, self.D3))
        D4_str = ','.join(map(str, self.D4))
        
        data = [
            last_part, second_to_last_part, self.surfaceAreaObj, self.compactnessObj, self.rectangularityObj, self.diameterObj, self.convexityObj, self.eccentricityObj, A3_str, D1_str, D2_str, D3_str, D4_str
        ]
        file_path = 'C:/Users/axelv/OneDrive/Desktop/MediaRetrieval/MultimediaRetrieval/steps/AxelHoekje/testingtest.csv'
        # Check if the file exists to write headers
        file_exists = os.path.isfile(file_path)    
        # Open the file in append mode
        with open(file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            # Write the headers if the file is new
            if not file_exists:
                writer.writerow(['name', 'class', 'surfaceAreaObj', 'compactnessObj', 'rectangularityObj', 'diameterObj', 'convexityObj', 'eccentricityObj', 'A3', 'D1', 'D2', 'D3', 'D4'])
            # Write the data as a new row
            writer.writerow(data)

    def load_obj(self, obj_file):
        vertices = []
        faces = []
        SurfaceArea = 0.0
        volume = 0.0
        with open(obj_file, 'r') as file:
            for line in file:
                if line.startswith('v '):
                    vertices.append(list(map(float, line.strip().split()[1:])))
                elif line.startswith('f '):
                    face = [int(idx.split('/')[0]) - 1 for idx in line.strip().split()[1:]]
                    faces.append(face)
                    # Calculate surface area and volume contribution of this face
                    v0, v1, v2 = [vertices[idx] for idx in face]
                    # Surface area calculation
                    triangle_area = np.linalg.norm(np.cross(np.array(v1) - np.array(v0), np.array(v2) - np.array(v0))) / 2
                    SurfaceArea += triangle_area
                    # Volume calculation using the signed volume of the tetrahedron
                    volume += np.dot(v0, np.cross(v1, v2)) / 6.0
        return np.array(vertices), np.array(faces), SurfaceArea, abs(volume), np.mean(vertices, axis=0)

    def calcSurfaceArea(self):
        return float(f"{self.SurfaceArea:.5f}")

    def calcCompactness(self):
        sphere_radius = (self.SurfaceArea / (4 * pi)) ** 0.5
        sphere_volume = (4/3) * pi * (sphere_radius ** 3)
        compactness = self.volume/sphere_volume
        return float(f"{compactness:.5f}")

    def calculate_convex_hull_volume(self):
        hull = ConvexHull(self.vertices)
        return hull.volume

    def calculate_eigenvalues(self):
        cov_matrix = np.cov(self.vertices.T)
        eigenvalues, _ = np.linalg.eig(cov_matrix)
        return eigenvalues

    def rectangularity(self):
        return float(f"{self.volume / self.obb_volume:.5f}")

    def diameter(self):
        hull = ConvexHull(self.vertices)
        hull_vertices = self.vertices[hull.vertices]
        # Find the maximum distance between any pair of hull vertices
        max_distance = 0
        num_hull_vertices = len(hull_vertices)
        for i in range(num_hull_vertices):
            for j in range(i + 1, num_hull_vertices):
                distance = np.linalg.norm(hull_vertices[i] - hull_vertices[j])
                if distance > max_distance:
                    max_distance = distance        
        return float(f"{max_distance:.5f}")

    def convexity(self):
        return float(f"{self.volume / self.convex_hull_volume :.5f}")

    def eccentricity(self):
        return float(f"{(max(self.eigenvalues) / min(self.eigenvalues)):.5f}")
    
    def calculate_obb_volume(self):
        # Step 1: Compute the covariance matrix
        mean = np.mean(self.vertices, axis=0)
        centered_points = self.vertices - mean
        covariance_matrix = np.cov(centered_points, rowvar=False)       
        # Step 2: Eigen decomposition
        eigenvalues, eigenvectors = np.linalg.eigh(covariance_matrix)        
        # Step 3: Rotate the points to align with the principal axes
        rotated_points = np.dot(centered_points, eigenvectors)        
        # Step 4: Find the extents
        min_extents = np.min(rotated_points, axis=0)
        max_extents = np.max(rotated_points, axis=0)        
        # Step 5: Calculate the volume of the OBB
        obb_extents = max_extents - min_extents
        obb_volume = np.prod(obb_extents) 
        return obb_volume
    
    def calculate_angle(self, v1, v2, v3):
        # Calculate vectors
        vec1 = v2 - v1
        vec2 = v3 - v1        
        # Calculate the magnitudes of the vectors
        norm_vec1 = np.linalg.norm(vec1)
        norm_vec2 = np.linalg.norm(vec2)    
        # Check for zero magnitude to avoid division by zero
        if norm_vec1 == 0 or norm_vec2 == 0:
            return 0.0  # or some other default value or handling       
        # Calculate the cosine of the angle using dot product
        cos_angle = np.dot(vec1, vec2) / (norm_vec1 * norm_vec2)        
        # Ensure the cosine value is within the valid range [-1, 1]
        cos_angle = np.clip(cos_angle, -1.0, 1.0)        
        # Calculate the angle in radians and then convert to degrees
        angle = np.arccos(cos_angle)
        angle_degrees = np.degrees(angle)        
        return angle_degrees

    def compute_A3(self, num_samples):
        angles = []
        for _ in range(num_samples):
            # Randomly select three distinct vertices
            v1, v2, v3 = random.sample(list(self.vertices), 3)
            # Calculate the angle between the three vertices
            angle = self.calculate_angle(np.array(v1), np.array(v2), np.array(v3))
            angles.append(angle)
        return angles

    def compute_D1(self, num_samples):
        barycenter = self.barycenter
        distances = []
        for _ in range(num_samples):
            # Randomly select a vertex
            random_vertex = random.choice(self.vertices)
            # Calculate the distance between the barycenter and the random vertex
            distance = np.linalg.norm(barycenter - random_vertex)
            distances.append(distance)    
        return distances
    
    def compute_D2(self, num_samples):
        distances = []
        for _ in range(num_samples):
            # Randomly select two distinct vertices
            v1, v2 = random.sample(list(self.vertices), 2)
            # Calculate the distance between the two vertices
            distance = np.linalg.norm(np.array(v1) - np.array(v2))
            distances.append(distance)      
        return distances
    
    def calculate_triangle_area(self, v1, v2, v3):
        # Calculate the area of the triangle using the cross product
        vec1 = np.array(v2) - np.array(v1)
        vec2 = np.array(v3) - np.array(v1)
        cross_product = np.cross(vec1, vec2)
        area = np.linalg.norm(cross_product) / 2
        return area

    def compute_D3(self, num_samples):
        areas = []
        for _ in range(num_samples):
            # Randomly select three distinct vertices
            v1, v2, v3 = random.sample(list(self.vertices), 3)            
            # Calculate the area of the triangle formed by the three vertices
            area = self.calculate_triangle_area(v1, v2, v3)
            areas.append(np.sqrt(area))
        return areas
    
    def calculate_tetrahedron_volume(self, v1, v2, v3, v4):
        # Calculate the volume of the tetrahedron using the determinant
        matrix = np.array([v2 - v1, v3 - v1, v4 - v1])
        volume = np.abs(np.linalg.det(matrix)) / 6
        return volume

    def compute_D4(self, num_samples):
        volumes = []     
        for _ in range(num_samples):
            # Randomly select four distinct vertices
            v1, v2, v3, v4 = random.sample(list(self.vertices), 4)           
            # Calculate the volume of the tetrahedron formed by the four vertices
            volume = self.calculate_tetrahedron_volume(v1, v2, v3, v4)
            volumes.append(np.cbrt(volume))        

            
        return volumes

    def compute_all_histograms(self):
        N = 100000
        numberBins = 93
        with multiprocessing.Pool(processes=5) as pool:
            results = pool.starmap(self.compute_histogram, [
                (self.compute_A3, N, numberBins),
                (self.compute_D1, N, numberBins),
                (self.compute_D2, N, numberBins),
                (self.compute_D3, N, numberBins),
                (self.compute_D4, N, numberBins)
            ])
        return results

    def compute_histogram(self, descriptor_func, num_samples, num_bins):
        values = descriptor_func(num_samples)
        histogram, bin_edges = np.histogram(values, bins=num_bins)
        histogram = histogram / np.sum(histogram)
        return histogram

