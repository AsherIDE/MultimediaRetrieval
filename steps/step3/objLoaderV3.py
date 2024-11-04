import sys
import os
import random
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog, QLineEdit, QSpacerItem, QHBoxLayout, QLabel, QSizePolicy
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtOpenGL import QGLWidget
from OpenGL.GL import *
from OpenGL.GLU import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from objectCalculatorWithThreads import ObjectCalculations  # Import the class from the other file



############################################################################################
# OpenGL widget
############################################################################################
class OpenGLWidget(QGLWidget):
    def __init__(self, parent=None):
        super(OpenGLWidget, self).__init__(parent)
        self.vertices = []
        self.faces = []
        self.display_faces = False
        self.display_edges = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateGL)
        self.timer.start(16)  # 16 is near 60 fps
        #voor de camera
        self.camera_pos = np.array([0.0, 0.0, -5.0])  # X, Y, Z position
        self.mouse_last_pos = None
        self.is_right_button_pressed = False  # Initialize the flag here 
        self.is_left_button_pressed = False #Left button standard false 
        # Object rotation angles
        self.rotation_x = 0
        self.rotation_y = 0
        #ObjectCalculator
        
        
        
############################################################################################
# Loading and reading the object file
############################################################################################
    def load_obj_file(self, fileName):
        self.vertices = []
        self.faces = []
        with open(fileName, 'r') as file:
            for line in file:
                if line.startswith('v '):
                    self.vertices.append(list(map(float, line.strip().split()[1:])))
                elif line.startswith('f '):
                    self.faces.append([int(idx.split('/')[0]) - 1 for idx in line.strip().split()[1:]])
        self.update()      

############################################################################################
# Rendering the objects *Lights in progress*
############################################################################################
    def initializeGL(self):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA) 
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glLightfv(GL_LIGHT0, GL_POSITION, [1, 1, 1, 0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glEnable(GL_LIGHT1)
        glLightfv(GL_LIGHT1, GL_POSITION, [-1, -1, -1, 0])
        glLightfv(GL_LIGHT1, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        glLightfv(GL_LIGHT1, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        glLightfv(GL_LIGHT1, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.5, 0.5, 0.5, 1.0])
        glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
        glMaterialf(GL_FRONT, GL_SHININESS, 50)
        glMatrixMode(GL_PROJECTION)
        gluPerspective(45, 1.33, 0.1, 50.0)
        glMatrixMode(GL_MODELVIEW)
        glTranslatef(0.0, 0.0, -5)

    #Painting the background
    def paintGL(self):
        glClearColor(0.878, 1.000, 1.000, 0.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        # Apply camera translation before rendering the object
        glLoadIdentity()  # Reset transformations
        glTranslatef(self.camera_pos[0], self.camera_pos[1], self.camera_pos[2]) 

        # Apply object rotation based on mouse input
        glRotatef(self.rotation_x, 1, 0, 0)  # Rotate around X-axis
        glRotatef(self.rotation_y, 0, 1, 0)  # Rotate around Y-axis
        self.draw_vertices()
        if self.display_faces:                    
            self.draw_faces()
        if self.display_edges:
            self.draw_edges() #voor nu nog even niet

    #Drawing the vertices   
    def draw_vertices(self):
        glBegin(GL_POINTS)
        glColor3f(1.0, 0.0, 1.0)
        for vertex in self.vertices:
            glVertex3fv(vertex)
        glEnd()

    # Drawing the edges
    def draw_edges(self):
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glEnable(GL_POLYGON_OFFSET_LINE)
        glPolygonOffset(-1.0, -1.0)
        glColor3f(0.0, 0.0, 0.0)  # Black color for edges
        glBegin(GL_TRIANGLES)
        for face in self.faces:
            for vertex_idx in face:
                glVertex3fv(self.vertices[vertex_idx])
        glEnd()
        glDisable(GL_POLYGON_OFFSET_LINE)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    #Drawing the faces
    def draw_faces(self):
        glBegin(GL_TRIANGLES)
        glColor4f(0.867, 0.627, 0.867, 0.8)
        for face in self.faces:
            for vertex_idx in face:
                glVertex3fv(self.vertices[vertex_idx])
        glEnd()

    #Toggle view
    def toggle_display_mode(self):
        self.display_faces = not self.display_faces
        self.update()

    def toggle_edges(self):
        self.display_edges = not self.display_edges
        self.update()

    #Getting the counts
    def get_vertices_count(self):
        return len(self.vertices)

    def get_faces_count(self):
        return len(self.faces)


############################################################################################
# Adding the mouse events
############################################################################################
    #Detecting pressed button (right)
    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.is_right_button_pressed = True
            self.mouse_last_pos = event.pos()
        elif event.button() == Qt.LeftButton:
            self.is_left_button_pressed = True
            self.mouse_last_pos = event.pos()


    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            self.is_right_button_pressed = False
        elif event.button() == Qt.LeftButton:
            self.is_left_button_pressed = False

    # Mouse move event to translate camera along X and Y axes
    def mouseMoveEvent(self, event):
        if self.is_right_button_pressed:
            dx = event.x() - self.mouse_last_pos.x()
            dy = event.y() - self.mouse_last_pos.y()

            # Sensitivity factor for camera movement
            sensitivity = 0.01

            # Update camera position along the X and Y axes based on mouse movement
            self.camera_pos[0] -= dx * sensitivity  # Move along X axis
            self.camera_pos[1] += dy * sensitivity  # Move along Y axis (inverted)

            self.mouse_last_pos = event.pos()  # Update the last mouse position

        elif self.is_left_button_pressed:
            dx = event.x() - self.mouse_last_pos.x()
            dy = event.y() - self.mouse_last_pos.y() 

             # Sensitivity for rotation
            rotation_sensitivity = 0.5

            # Update rotation angles for object
            self.rotation_x += dy * rotation_sensitivity  # Rotate around X-axis (up/down)
            self.rotation_y += dx * rotation_sensitivity  # Rotate around Y-axis (left/right)

            self.mouse_last_pos = event.pos()  # Update the last mouse position

    def wheelEvent(self, event):
        zoom_sensitivity = 0.35  # Adjust sensitivity as needed
        delta = event.angleDelta().y()  # Get the scroll amount
    
        if delta > 0:
            self.camera_pos[2] += zoom_sensitivity  # Zoom out
        else:
            self.camera_pos[2] -= zoom_sensitivity  # Zoom in    
        self.update()  # Update the view


############################################################################################
# Histogram window showcasing all the distributions of the object
############################################################################################
class HistogramWindow(QWidget):
    def __init__(self, obj_calc):
        super().__init__()
        self.obj_calc = obj_calc
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        num_samples = 1000
        num_bins = 30
        # Create histograms for each descriptor
        self.create_histogram(self.obj_calc.compute_histogram(self.obj_calc.compute_A3, num_samples, num_bins), 'A3 angle between 3 random vertices', 'Angle (degrees)', layout)
        self.create_histogram(self.obj_calc.compute_histogram(self.obj_calc.compute_D1, num_samples, num_bins), 'D1 distance between barycenter and random vertex', 'Distance', layout)
        self.create_histogram(self.obj_calc.compute_histogram(self.obj_calc.compute_D2, num_samples, num_bins), 'D2 distance between 2 random vertices', 'Distance', layout)
        self.create_histogram(self.obj_calc.compute_histogram(self.obj_calc.compute_D3, num_samples, num_bins), 'D3 square root of area of triangle given by 3 random vertices', 'Square Root of Area', layout)
        self.create_histogram(self.obj_calc.compute_histogram(self.obj_calc.compute_D4, num_samples, num_bins), 'D4 cube root of volume of tetrahedron formed by 4 random vertices', 'Cube Root of Volume', layout)    
        self.setLayout(layout)
        self.setWindowTitle('Histograms of Descriptors')
        self.show()

    def create_histogram(self, histogram, title, xlabel, layout):
        fig, ax = plt.subplots()
        ax.bar(range(len(histogram)), histogram, width=1.0, edgecolor='black')
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel('Normalized Frequency')
        
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)


############################################################################################
# Window (in which OpenGL widget exists)
############################################################################################
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Object testing')
        self.setGeometry(100, 100, 900, 600)
        self.opengl_widget = OpenGLWidget(self)
        self.shape = None        
    
        # Create side panel with buttons
        self.side_panel = QWidget(self)
        self.side_layout = QVBoxLayout(self.side_panel)
        self.side_panel.setFixedWidth(240)
        
        # Open file button
        self.button = QPushButton('Open OBJ File', self)
        self.button.clicked.connect(self.open_file_dialog)
        self.side_layout.addWidget(self.button)
        
        # Text box to display chosen file
        self.file_label = QLabel('The loaded file:', self)
        self.side_layout.addWidget(self.file_label)
        self.file_display = QLineEdit(self)
        self.file_display.setReadOnly(True)
        self.side_layout.addWidget(self.file_display)
        self.side_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # Toggle button faces/vertices
        self.toggle_button = QPushButton('Toggle vertices/faces', self)
        self.toggle_button.clicked.connect(self.opengl_widget.toggle_display_mode)
        self.side_layout.addWidget(self.toggle_button)

        # Toggle button edges
        self.toggle_button_edges = QPushButton('Toggle edges; causes lag for high F-count', self)
        self.toggle_button_edges.clicked.connect(self.opengl_widget.toggle_edges)
        self.side_layout.addWidget(self.toggle_button_edges)

        # Text boxes to display vertices and faces count
        self.vertices_label = QLabel('Vertices count:', self)
        self.side_layout.addWidget(self.vertices_label)
        self.vertices_display = QLineEdit(self)
        self.vertices_display.setReadOnly(True)
        self.side_layout.addWidget(self.vertices_display)
        
        self.faces_label = QLabel('Faces count:', self)
        self.side_layout.addWidget(self.faces_label)
        self.faces_display = QLineEdit(self)
        self.faces_display.setReadOnly(True)
        self.side_layout.addWidget(self.faces_display)

        # Button to show histograms
        self.histogram_button = QPushButton('Show Histograms', self)
        self.histogram_button.clicked.connect(self.show_histograms)
        self.side_layout.addWidget(self.histogram_button)

        # Main layout + spacing the buttons
        self.side_layout.addStretch()
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.opengl_widget, 3)  # Stretch factor to make OpenGL widget larger
        main_layout.addWidget(self.side_panel)     # Stretch factor to make side panel smaller 

        # Bottom panel for object calculations
        self.bottom_panel = QWidget(self)
        self.bottom_layout = QHBoxLayout(self.bottom_panel)
        
        self.surfaceArea_display = QLabel('Surface Area')
        self.bottom_layout.addWidget(self.surfaceArea_display)
        
        self.compactness_display = QLabel('Compactness')
        self.bottom_layout.addWidget(self.compactness_display)
        
        self.rectangularity_display = QLabel('3D Rectangularity')
        self.bottom_layout.addWidget(self.rectangularity_display)
        
        self.diameter_display = QLabel('Diameter')
        self.bottom_layout.addWidget(self.diameter_display)
        
        self.convexity_display = QLabel('Convexity')
        self.bottom_layout.addWidget(self.convexity_display)

        self.eccentricity_display = QLabel('Eccentricity')
        self.bottom_layout.addWidget(self.eccentricity_display)

        labels = [
            self.surfaceArea_display,
            self.compactness_display,
            self.rectangularity_display,
            self.diameter_display,
            self.convexity_display,
            self.eccentricity_display
        ]
        
        for label in labels:
            label.setStyleSheet("border: 1px solid black; padding: 5px;")
            self.bottom_layout.addWidget(label)
        
        # Add bottom panel to main layout
        main_layout_with_bottom = QVBoxLayout()
        main_layout_with_bottom.addLayout(main_layout)
        main_layout_with_bottom.addWidget(self.bottom_panel)
        
        container = QWidget()
        container.setLayout(main_layout_with_bottom)
        self.setCentralWidget(container)
        
############################################################################################
#Functions for local descriptors and global descriptors as histograms
############################################################################################
    def calcSurfaceArea(self):
        self.surfaceArea_display.setText(f'Surface Area: {self.shape.surfaceAreaObj}')

    def calcCompactness(self):
        self.compactness_display.setText(f'Compactness: {self.shape.compactnessObj}')

    def calcRectangularity(self):
        self.rectangularity_display.setText(f'3D Rectangularity: {self.shape.rectangularity()}')

    def calcDiameter(self):
        self.diameter_display.setText(f'Diameter: {self.shape.diameter()}')

    def calcConvexity(self):
        self.convexity_display.setText(f'Convexity: {self.shape.convexity()}')

    def calcEccentricity(self):
        self.eccentricity_display.setText(f'Eccentricity: {self.shape.eccentricity()}')

    # Function for opening the file and setting all stats according to the file
    def open_file_dialog(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open OBJ File", "", "OBJ Files (*.obj);;All Files (*)", options=options)
        if fileName:
            self.opengl_widget.load_obj_file(fileName)
            self.file_display.setText(fileName)
            self.vertices_display.setText(str(self.opengl_widget.get_vertices_count()))
            self.faces_display.setText(str(self.opengl_widget.get_faces_count()))
            self.shape = ObjectCalculations(fileName)
            # Getting the stats
            self.calcSurfaceArea()
            self.calcCompactness()
            self.calcRectangularity()
            self.calcDiameter()
            self.calcConvexity()
            self.calcEccentricity()
            self.calcDiameter()
            self.shape.write_to_csv()

    def show_histograms(self):
        if self.shape:
            num_samples = 1  # Example value
            num_bins = 1  # Example value
            histograms = self.shape.compute_all_descriptors(num_samples, num_bins)
            self.histogram_window = HistogramWindow(histograms)
            self.histogram_window.show()

# execution of the program
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())