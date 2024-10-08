import numpy as np
import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename

class ShapeNormalizer:
    def __init__(self):
        self.vertices = []
        self.faces = []

    def load_obj_file(self, fileName):
        self.vertices = []
        self.faces = []
        with open(fileName, 'r') as file:
            for line in file:
                if line.startswith('v '):  # Read vertex
                    self.vertices.append(list(map(float, line.strip().split()[1:])))
                elif line.startswith('f '):  # Read face
                    self.faces.append([int(idx.split('/')[0]) - 1 for idx in line.strip().split()[1:]])
        self.vertices = np.array(self.vertices)  # Convert to numpy array for easier manipulation

    def update(self):
        pass  # You can add any real-time viewer updates here if needed

    def normalize_shape(self):
        # Center the shape at the origin
        self.center_shape()
        # Scale the shape to fit inside a unit cube
        self.scale_shape()
        # Align the shape using PCA
        self.align_shape()
        # Flip the shape using moment tests
        self.flip_shape()
        # Update after all transformations
        self.update()

    def center_shape(self):
        """Translate the shape to center it at the origin."""
        centroid = self.vertices.mean(axis=0)
        self.vertices -= centroid

    def scale_shape(self):
        """Scale the shape so the farthest vertex from the origin is at a distance of 1."""
        max_distance = np.max(np.linalg.norm(self.vertices, axis=1))
        scale_factor = 1.0 / max_distance
        self.vertices *= scale_factor

    def align_shape(self):
        """Align the shape using PCA (Principal Component Analysis)."""
        # Compute the covariance matrix
        covariance_matrix = np.cov(self.vertices.T)

        # Eigen decomposition of the covariance matrix
        eigenvalues, eigenvectors = np.linalg.eigh(covariance_matrix)

        # Sort eigenvalues and eigenvectors in descending order of eigenvalues
        sorted_indices = np.argsort(eigenvalues)[::-1]
        sorted_eigenvectors = eigenvectors[:, sorted_indices]

        # Rotate the vertices so that the eigenvectors align with the x, y, and z axes
        self.vertices = np.dot(self.vertices, sorted_eigenvectors)

    def flip_shape(self):
        """Flip the shape along each axis based on the moment test."""
        # Compute the first moment (mean of the coordinates) for each axis
        moments = self.vertices.mean(axis=0)

        # Flip the vertices along each axis if the moment is negative
        for i in range(3):  # For each axis (x, y, z)
            if moments[i] < 0:
                self.vertices[:, i] *= -1

    def save_obj_file(self, output_filepath):
        with open(output_filepath, 'w') as file:
            for vertex in self.vertices:
                file.write(f"v {vertex[0]} {vertex[1]} {vertex[2]}\n")
            for face in self.faces:
                face_str = " ".join([str(idx + 1) for idx in face])
                file.write(f"f {face_str}\n")

    def process_all_shapes(self, input_folder, output_folder):
        os.makedirs(output_folder, exist_ok=True)
        obj_files = []
        for root, dirs, files in os.walk(input_folder):
            for file in files:
                if file.lower().endswith('.obj'):  # Case-insensitive check for .obj files
                    obj_files.append(os.path.join(root, file))

        if not obj_files:
            print("No .obj files found in the input folder!")
            return

        for obj_file in obj_files:
            relative_path = os.path.relpath(obj_file, input_folder)
            output_filepath = os.path.join(output_folder, relative_path.replace('.obj', '_normalized.obj'))

            os.makedirs(os.path.dirname(output_filepath), exist_ok=True)

            print(f"Processing {obj_file}")
            self.load_obj_file(obj_file)
            self.normalize_shape()
            self.save_obj_file(output_filepath)
            print(f"Saved normalized file to {output_filepath}")
            print('-' * 40)

    def select_and_normalize_single_file(self, output_folder):
        """Allow user to select a single .obj file and normalize it."""
        # Hide the main tkinter window
        root = Tk()
        root.withdraw()

        # Open file dialog to select a file
        file_path = askopenfilename(
            filetypes=[("OBJ files", "*.obj")],
            title="Select an OBJ file"
        )

        if not file_path:
            print("No file selected!")
            return

        # Process the selected file
        print(f"Processing {file_path}")
        self.load_obj_file(file_path)

        # Normalize the shape
        self.normalize_shape()

        # Create output file path
        filename = os.path.basename(file_path).replace('.obj', '_normalized.obj')
        output_filepath = os.path.join(output_folder, filename)

        # Save normalized shape
        os.makedirs(output_folder, exist_ok=True)
        self.save_obj_file(output_filepath)
        print(f"Saved normalized file to {output_filepath}")




#either choose process all shapes or normalize single file depending on what you need.  Change input and output folders as well. 1


input_folder = r'C:\Users\axelv\OneDrive\Desktop\MediaRetrieval\MultimediaRetrieval\ShapeDatabase_INFOMR-resampled'
output_folder = r'C:\Users\axelv\OneDrive\Desktop\MediaRetrieval\MultimediaRetrieval\NormalizedShapes-resampled' 


#single_output_folder = r'C:\Universiteit\HCI\MultimediaRetrieval\SingleNormalizedShapes'


normalizer = ShapeNormalizer()
#normalizer.select_and_normalize_single_file(single_output_folder) 
normalizer.process_all_shapes(input_folder, output_folder)