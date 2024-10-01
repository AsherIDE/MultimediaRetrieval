import numpy as np
from scipy.spatial import ConvexHull
from math import pi

class ObjectCalculations:
    def __init__(self, obj_file):
        self.vertices, self.faces, self.SurfaceArea, self.volume = self.load_obj(obj_file)
        self.surfaceArea = self.calcSurfaceArea()
        self.objCompactness = self.calcCompactness()
        self.convex_hull_volume = self.calculate_convex_hull_volume()
        self.eigenvalues = self.calculate_eigenvalues()
        self.obb_volume = self.calculate_obb_volume()

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
        return np.array(vertices), np.array(faces), SurfaceArea, abs(volume)

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

    def compactness(self):
        return (self.volume ** 2) / (self.SurfaceArea ** 3)

    def rectangularity(self):
        return float(f"{self.volume / self.obb_volume:.5f}")

    def diameter(self):
        max_distance = 0
        for i in range(len(self.vertices)):
            for j in range(i + 1, len(self.vertices)):
                distance = np.linalg.norm(self.vertices[i] - self.vertices[j])
                if distance > max_distance:
                    max_distance = distance
        return max_distance

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