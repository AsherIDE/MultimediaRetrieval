import numpy as np
import matplotlib.pyplot as plt

class ShapeVisualizer:
    def __init__(self):
        self.vertices = []

    def load_obj_file(self, file_path):
        """Load vertices from an OBJ file."""
        self.vertices = []
        with open(file_path, 'r') as file:
            for line in file:
                if line.startswith('v '):  # Read vertex
                    self.vertices.append(list(map(float, line.strip().split()[1:])))
        self.vertices = np.array(self.vertices)  # Convert to numpy array for easier manipulation

    def visualize_shapes(self, original_vertices, normalized_vertices):
        """Visualize the original and normalized shapes in a 3D plot."""
        fig = plt.figure(figsize=(12, 6))
        
        # Original shape
        ax1 = fig.add_subplot(121, projection='3d')
        ax1.scatter(original_vertices[:, 0], original_vertices[:, 1], original_vertices[:, 2], c='blue', marker='o', alpha=0.5)
        ax1.set_title('Original Shape')
        ax1.set_xlabel('X axis')
        ax1.set_ylabel('Y axis')
        ax1.set_zlabel('Z axis')
        
        # Normalized shape
        ax2 = fig.add_subplot(122, projection='3d')
        ax2.scatter(normalized_vertices[:, 0], normalized_vertices[:, 1], normalized_vertices[:, 2], c='green', marker='o', alpha=0.5)
        ax2.set_title('Normalized Shape')
        ax2.set_xlabel('X axis')
        ax2.set_ylabel('Y axis')
        ax2.set_zlabel('Z axis')

        plt.tight_layout()
        plt.show()

# Paths to the OBJ files
before_file_path = r'C:\Universiteit\HCI\ShapeDatabase_INFOMR-resampled\Bicycle\D00016.obj'  # Non-normalized OBJ file path
after_file_path = r'C:\Universiteit\HCI\NormalizedShapes-resampled\Bicycle\D00016_normalized.obj'  # Normalized OBJ file path

# Load original and normalized shapes
visualizer = ShapeVisualizer()

# Load the original shape
visualizer.load_obj_file(before_file_path)
original_vertices = visualizer.vertices.copy()

# Load the normalized shape
visualizer.load_obj_file(after_file_path)
normalized_vertices = visualizer.vertices.copy()

# Visualize shapes
visualizer.visualize_shapes(original_vertices, normalized_vertices)
