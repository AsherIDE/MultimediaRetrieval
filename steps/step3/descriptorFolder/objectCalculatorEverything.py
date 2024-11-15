import numpy as np
import random
import csv
import os
from scipy.spatial import ConvexHull
from math import pi
import trimesh
class ObjectCalculations:
    def __init__(self, obj_file):
        self.obj_file = obj_file
        self.vertices, self.faces, self.SurfaceArea, self.volume, self.barycenter = self.load_obj(obj_file)
        self.convex_hull_volume = self.calculate_convex_hull_volume()
        self.eigenvalues = self.calculate_eigenvalues()
        self.obb_volume = self.calculate_obb_volume()
        self.compactnessObj = self.calcCompactness()
        self.rectangularityObj = self.rectangularity()
        self.convexityObj = self.convexity()
        
    def write_to_csv(self):
        # Summarize the lists by taking their mean
        last_part = os.path.basename(self.obj_file)
    
        # Get the part before the last part (directory name)
        second_to_last_part = os.path.basename(os.path.dirname(self.obj_file))       
        data = [
            last_part, second_to_last_part, self.compactnessObj, self.rectangularityObj, self.convexityObj
        ]
        file_path = 'newVolumeMetrics.csv'
        # Check if the file exists to write headers
        file_exists = os.path.isfile(file_path)    
        # Open the file in append mode
        with open(file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            # Write the headers if the file is new
            if not file_exists:
                writer.writerow(['name', 'class', 'compactnessObj','rectangularityObj','convexityObj'])
            # Write the data as a new row
            writer.writerow(data)

    def load_obj(self, obj_file):
        vertices = []
        faces = []
        SurfaceArea = 0.0
        volume = self.getVolume(obj_file)
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
                    #volume += np.dot(v0, np.cross(v1, v2)) / 6.0
        return np.array(vertices), np.array(faces), SurfaceArea, abs(volume), np.mean(vertices, axis=0)

    def getVolume(self, obj_file):
        mesh = trimesh.load(obj_file)
        volume = mesh.volume
        return volume
    
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
        print('Started A3')
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
        print('Started D1')
        for  v in self.vertices:
            # Calculate the distance between the barycenter and the random vertex
            distance = np.linalg.norm(barycenter - v)
            distances.append(distance)    
        return distances
    
    def compute_D2(self, num_samples):
        distances = []
        ('Started D2')
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
        ('Started D3')
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
        ('Started D4')      
        for _ in range(self.vertices):
            # Randomly select four distinct vertices
            v1, v2, v3, v4 = random.sample(list(self.vertices), 4)           
            # Calculate the volume of the tetrahedron formed by the four vertices
            volume = self.calculate_tetrahedron_volume(v1, v2, v3, v4)
            volumes.append(np.cbrt(volume))        

            
        return volumes

    def compute_histogram(self, descriptor_func, num_samples, num_bins):
            #GrabData
            values = descriptor_func(num_samples)            
            #Fixed bins
            histogram, bin_edges = np.histogram(values, bins=num_bins)            
            #Normalize
            histogram = histogram / np.sum(histogram)            
            return histogram

def process_folder(folder_path):
    # Walk through the directory tree
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if filename.endswith('.obj'):
                obj_file_path = os.path.join(root, filename)
                obj_file_path = os.path.normpath(obj_file_path)  # Normalize the path
                print(f"Processing file: {obj_file_path}")
                # Create an instance of ObjectCalculations for each OBJ file
                obj_calc = ObjectCalculations(obj_file_path)
                # Write the descriptors to the CSV file
                obj_calc.write_to_csv()

def process_file(folder_path):
    # Walk through the directory tree
    if folder_path.endswith('.obj'):
        obj_file_path = folder_path
        obj_file_path = os.path.normpath(obj_file_path)  # Normalize the path
        print(f"Processing file: {obj_file_path}")
        # Create an instance of ObjectCalculations for each OBJ file
        obj_calc = ObjectCalculations(obj_file_path)
        # Write the descriptors to the CSV file
        obj_calc.write_to_csv()

#Remove #s to do all the normalized shapes
folder_path = 'MultimediaRetrieval/NormalizedShapes-resampled'
process_folder(folder_path)