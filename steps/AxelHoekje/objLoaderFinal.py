import sys
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QDialog, QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog, QLineEdit, QSpacerItem, QHBoxLayout, QLabel, QSizePolicy
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtOpenGL import QGLWidget
from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5.QtGui import QFont
import numpy as np
from singleObjectCalcFinal import ObjectCalculations
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

class SmallerWidget(QGLWidget):
    def __init__(self, parent=None):
        super(SmallerWidget, self).__init__(parent)
        self.vertices = []
        self.faces = []
        self.display_vertices = False
        self.display_faces = False
        self.display_edges = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateGL)
        self.timer.start(16)  # 16 is near 60 fps
        self.camera_pos = np.array([-3.6, -2.2, -8.0])  # X, Y, Z position
        self.mouse_last_pos = None
        self.is_right_button_pressed = False  # Initialize the flag here 
        self.is_left_button_pressed = False #Left button standard false 
        # Object rotation angles
        self.rotation_x = 90
        self.rotation_y = 0

        
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
        gluPerspective(45, 1.33, 0.1, 50)
        glMatrixMode(GL_MODELVIEW)
        glTranslatef(self.camera_pos[0], self.camera_pos[1], self.camera_pos[2])

    def paintGL(self):
        glClearColor(1.0, 1.000, 1.000, 0.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(self.camera_pos[0], self.camera_pos[1], self.camera_pos[2]) 
        glRotatef(self.rotation_x, 1, 0, 0)  
        glRotatef(self.rotation_y, 0, 1, 0)  
        if self.display_vertices:
            self.draw_vertices()
        if self.display_faces:                    
            self.draw_faces()
        if self.display_edges:
            self.draw_edges()

    def draw_vertices(self):
        glBegin(GL_POINTS)
        glColor3f(0.412, 0.412, 0.412)
        for vertex in self.vertices:
            glVertex3fv(vertex)
        glEnd()

    def draw_edges(self):
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glEnable(GL_POLYGON_OFFSET_LINE)
        glPolygonOffset(-1.0, -1.0)
        glColor3f(0.0, 0.0, 0.0)  
        glBegin(GL_TRIANGLES)
        for face in self.faces:
            for vertex_idx in face:
                glVertex3fv(self.vertices[vertex_idx])
        glEnd()
        glDisable(GL_POLYGON_OFFSET_LINE)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    def draw_faces(self):
        glBegin(GL_TRIANGLES)
        glColor4f(0.502, 0.502, 0.502, 0.8)
        for face in self.faces:
            for vertex_idx in face:
                glVertex3fv(self.vertices[vertex_idx])
        glEnd()


    def toggle_vertices(self):
        self.display_vertices = not self.display_vertices
        self.update()

    def toggle_faces(self):
        self.display_faces = not self.display_faces
        self.update()


    def toggle_edges_on(self):
        self.display_edges = True
        self.update()

    def toggle_edges_off(self):
        self.display_edges = False
        self.update()

    def get_vertices_count(self):
        return len(self.vertices)

    def get_faces_count(self):
        return len(self.faces)

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

    def mouseMoveEvent(self, event):
        if self.is_right_button_pressed:
            dx = event.x() - self.mouse_last_pos.x()
            dy = event.y() - self.mouse_last_pos.y()
            sensitivity = 0.01
            self.camera_pos[0] -= dx * sensitivity  
            self.camera_pos[1] += dy * sensitivity  
            self.mouse_last_pos = event.pos()  
        elif self.is_left_button_pressed:
            dx = event.x() - self.mouse_last_pos.x()
            dy = event.y() - self.mouse_last_pos.y() 
            rotation_sensitivity = 0.5
            self.rotation_x += dy * rotation_sensitivity  
            self.rotation_y += dx * rotation_sensitivity  
            self.mouse_last_pos = event.pos()  

    def wheelEvent(self, event):
        zoom_sensitivity = 0.35  
        delta = event.angleDelta().y()  
        if delta > 0:
            self.camera_pos[2] += zoom_sensitivity  
        else:
            self.camera_pos[2] -= zoom_sensitivity  
        self.update() 

############################################################################################
# OpenGL widget
############################################################################################
class OpenGLWidget(QGLWidget):
    def __init__(self, parent=None):
        super(OpenGLWidget, self).__init__(parent)
        self.vertices = []
        self.faces = []
        self.display_vertices = False
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
        gluPerspective(45, 1.33, 0.1, 50)
        glMatrixMode(GL_MODELVIEW)
        glTranslatef(self.camera_pos[0], self.camera_pos[1], self.camera_pos[2])

    def paintGL(self):
        glClearColor(1.0, 1.000, 1.000, 0.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(self.camera_pos[0], self.camera_pos[1], self.camera_pos[2]) 
        glRotatef(self.rotation_x, 1, 0, 0)  
        glRotatef(self.rotation_y, 0, 1, 0)  
        if self.display_vertices:
            self.draw_vertices()
        if self.display_faces:                    
            self.draw_faces()
        if self.display_edges:
            self.draw_edges()

    def draw_vertices(self):
        glBegin(GL_POINTS)
        glColor3f(0.412, 0.412, 0.412)
        for vertex in self.vertices:
            glVertex3fv(vertex)
        glEnd()

    def draw_edges(self):
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glEnable(GL_POLYGON_OFFSET_LINE)
        glPolygonOffset(-1.0, -1.0)
        glColor3f(0.0, 0.0, 0.0)  
        glBegin(GL_TRIANGLES)
        for face in self.faces:
            for vertex_idx in face:
                glVertex3fv(self.vertices[vertex_idx])
        glEnd()
        glDisable(GL_POLYGON_OFFSET_LINE)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    def draw_faces(self):
        glBegin(GL_TRIANGLES)
        glColor4f(0.502, 0.502, 0.502, 0.8)
        for face in self.faces:
            for vertex_idx in face:
                glVertex3fv(self.vertices[vertex_idx])
        glEnd()


    def toggle_vertices(self):
        self.display_vertices = not self.display_vertices
        self.update()

    def toggle_faces(self):
        self.display_faces = not self.display_faces
        self.update()


    def toggle_edges_on(self):
        self.display_edges = True
        self.update()

    def toggle_edges_off(self):
        self.display_edges = False
        self.update()

    def get_vertices_count(self):
        return len(self.vertices)

    def get_faces_count(self):
        return len(self.faces)

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

    def mouseMoveEvent(self, event):
        if self.is_right_button_pressed:
            dx = event.x() - self.mouse_last_pos.x()
            dy = event.y() - self.mouse_last_pos.y()
            sensitivity = 0.01
            self.camera_pos[0] -= dx * sensitivity  
            self.camera_pos[1] += dy * sensitivity  
            self.mouse_last_pos = event.pos()  
        elif self.is_left_button_pressed:
            dx = event.x() - self.mouse_last_pos.x()
            dy = event.y() - self.mouse_last_pos.y() 
            rotation_sensitivity = 0.5
            self.rotation_x += dy * rotation_sensitivity  
            self.rotation_y += dx * rotation_sensitivity  
            self.mouse_last_pos = event.pos()  

    def wheelEvent(self, event):
        zoom_sensitivity = 0.35  
        delta = event.angleDelta().y()  
        if delta > 0:
            self.camera_pos[2] += zoom_sensitivity  
        else:
            self.camera_pos[2] -= zoom_sensitivity  
        self.update()  

############################################################################################
# Window (in which OpenGL widget exists)
############################################################################################
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Object testing')
    
        self.opengl_widget = OpenGLWidget(self)
        self.opengl_widget.setFixedSize(1650, 600)  # Set fixed size for the OpenGL widget

        self.opengl_widgets_small = [SmallerWidget(self) for _ in range(5)]
        for widget in self.opengl_widgets_small:
            widget.setFixedSize(300, 300)

        hbox = QHBoxLayout()
        for widget in self.opengl_widgets_small:
            hbox.addWidget(widget)

        #Create side panel with buttons
        self.side_panel = QWidget(self)
        self.side_layout = QVBoxLayout(self.side_panel)
        self.side_panel.setFixedWidth(240)

        # Title label
        self.querying_label = QLabel('Querying', self)
        self.querying_label.setAlignment(Qt.AlignCenter)  # Center the text
        font = QFont()
        font.setBold(True)
        self.querying_label.setFont(font)
        self.side_layout.addWidget(self.querying_label)

        #Open file button
        self.button = QPushButton('Load OBJ File', self)
        self.button.clicked.connect(self.open_file_dialog)
        self.side_layout.addWidget(self.button)
        
        #Text box to display chosen file
        self.file_label = QLabel('The loaded file:', self)
        font = QFont()
        font.setBold(True)
        self.file_label.setFont(font)
        self.side_layout.addWidget(self.file_label)
        self.file_display = QLineEdit(self)
        self.file_display.setReadOnly(True)
        self.side_layout.addWidget(self.file_display)
        self.side_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        #Label display options
        self.options_label = QLabel('Display:', self)
        font = QFont()
        font.setBold(True)
        self.options_label.setFont(font)
        self.side_layout.addWidget(self.options_label)

        # Create a horizontal layout for the edges buttons
        self.vertices_faces_layout = QHBoxLayout()
        # Toggle vertices button
        self.vertices_button = QPushButton('Vertices', self)
        self.vertices_button.clicked.connect(self.opengl_widget.toggle_vertices)
        self.vertices_faces_layout.addWidget(self.vertices_button)
        # Toggle faces button
        self.faces_button = QPushButton('Faces', self)
        self.faces_button.clicked.connect(self.opengl_widget.toggle_faces)
        self.vertices_faces_layout.addWidget(self.faces_button)
        self.side_layout.addLayout(self.vertices_faces_layout)

        # Create a horizontal layout for the edges buttons
        self.edges_layout = QHBoxLayout()
        # Edges On button
        self.edges_on_button = QPushButton('Edges On', self)
        self.edges_on_button.clicked.connect(self.opengl_widget.toggle_edges_on)
        self.edges_layout.addWidget(self.edges_on_button)
        # Edges Off button
        self.edges_off_button = QPushButton('Edges Off', self)
        self.edges_off_button.clicked.connect(self.opengl_widget.toggle_edges_off)
        self.edges_layout.addWidget(self.edges_off_button)        
        self.side_layout.addLayout(self.edges_layout)

        #Object stats
        self.desc_label = QLabel('Options:', self)
        font = QFont()
        font.setBold(True)
        self.desc_label.setFont(font)
        self.side_layout.addWidget(self.desc_label)

        #Simple search similar objects
        self.simple_search_button = QPushButton('Find similar objects (simple)', self)
        self.simple_search_button.clicked.connect(self.perform_simple_search)
        self.side_layout.addWidget(self.simple_search_button)
        
        #Simple objects advanced
        self.adv_search_button = QPushButton('Find similar objects (simple)', self)
        self.adv_search_button.clicked.connect(self.perform_adv_search)
        self.side_layout.addWidget(self.adv_search_button)
        
        #Show feature histograms
        self.global_descriptors_button = QPushButton('Show global descriptors', self)
        self.global_descriptors_button.clicked.connect(self.show_global_descriptors)
        self.side_layout.addWidget(self.global_descriptors_button)

        #Object stats
        self.stats_label = QLabel('Object statistics', self)
        self.stats_label.setAlignment(Qt.AlignCenter)  # Center the text
        font = QFont()
        font.setBold(True)
        self.stats_label.setFont(font)
        self.side_layout.addWidget(self.stats_label)

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

        # Additional text boxes for other statistics
        self.surface_area_label = QLabel('Surface Area:', self)
        self.side_layout.addWidget(self.surface_area_label)
        self.surface_area_display = QLineEdit(self)
        self.surface_area_display.setReadOnly(True)
        self.side_layout.addWidget(self.surface_area_display)

        self.volume_label = QLabel('Volume:', self)
        self.side_layout.addWidget(self.volume_label)
        self.volume_display = QLineEdit(self)
        self.volume_display.setReadOnly(True)
        self.side_layout.addWidget(self.volume_display)

        self.compactness_label = QLabel('Compactness:', self)
        self.side_layout.addWidget(self.compactness_label)
        self.compactness_display = QLineEdit(self)
        self.compactness_display.setReadOnly(True)
        self.side_layout.addWidget(self.compactness_display)

        self.rectangularity_label = QLabel('3D Rectangularity:', self)
        self.side_layout.addWidget(self.rectangularity_label)
        self.rectangularity_display = QLineEdit(self)
        self.rectangularity_display.setReadOnly(True)
        self.side_layout.addWidget(self.rectangularity_display)

        self.diameter_label = QLabel('Diameter:', self)
        self.side_layout.addWidget(self.diameter_label)
        self.diameter_display = QLineEdit(self)
        self.diameter_display.setReadOnly(True)
        self.side_layout.addWidget(self.diameter_display)

        self.convexity_label = QLabel('Convexity:', self)
        self.side_layout.addWidget(self.convexity_label)
        self.convexity_display = QLineEdit(self)
        self.convexity_display.setReadOnly(True)
        self.side_layout.addWidget(self.convexity_display)

        self.eccentricity_label = QLabel('Eccentricity:', self)
        self.side_layout.addWidget(self.eccentricity_label)
        self.eccentricity_display = QLineEdit(self)
        self.eccentricity_display.setReadOnly(True)
        self.side_layout.addWidget(self.eccentricity_display)
        
        # Create the main layout
        main_layout = QVBoxLayout()
        
        # Top layout with the main OpenGL widget and side panel
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.opengl_widget, 0, Qt.AlignTop | Qt.AlignLeft)
        top_layout.addWidget(self.side_panel)

        # Add the top layout and the horizontal layout for small widgets to the main layout
        main_layout.addLayout(top_layout)
        main_layout.addStretch()  # Add stretch to push the row to the bottom
        main_layout.addLayout(hbox)

        # Set the main layout to the central widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        self.showMaximized()  # Open the application in maximized window

    #Define the method to perform simple search
    def perform_simple_search(self):
        allDescriptors = self.shape.getAllDescriptors()
        print(allDescriptors)

    def perform_adv_search(self):
        print("Advanced search")

    # Define the method to handle the button click
    def show_global_descriptors(self):
        if hasattr(self, 'shape'):
            descriptors = self.shape.getGlobalDescriptors()
            self.plot_descriptors(descriptors)
        else:
            QMessageBox.warning(self, "Warning", "No object loaded. Please load an OBJ file first.")

    def plot_descriptors(self, descriptors):
        A3, D1, D2, D3, D4 = descriptors

        # Create a new dialog window
        dialog = QDialog(self)
        dialog.setWindowTitle("Global Descriptors Frequency plots N=100k and B=93")
        layout = QVBoxLayout(dialog)

        # Create the plot
        fig, axs = plt.subplots(3, 2, figsize=(10, 10))
        axs = axs.flatten()

        axs[0].plot(A3)
        axs[0].set_title('A3: angle between 3 random vertices')

        axs[1].plot(D1)
        axs[1].set_title('D1: distance between barycenter and random vertex')

        axs[2].plot(D2)
        axs[2].set_title('D2: distance between 2 random vertices')

        axs[3].plot(D3)
        axs[3].set_title('D3: square root of area of triangle given by 3 random vertices')

        axs[4].plot(D4)
        axs[4].set_title('D4: cube root of volume of tetrahedron formed by random vertices')

        # Hide the empty subplot
        fig.delaxes(axs[5])

        plt.tight_layout()
        # Add the plot to the dialog
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)
        dialog.setLayout(layout)
        dialog.exec_()

    def displaySmallerWidgets(self, filePath):
        for widget in self.opengl_widgets_small:
            print(widget)
            print(filePath)
            widget.load_obj_file(filePath)
            widget.toggle_vertices()
            widget.toggle_vertices()
            widget.toggle_edges_on()

    # Function for opening the file and setting all stats according to the file
    def open_file_dialog(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open OBJ File", "", "OBJ Files (*.obj);;All Files (*)", options=options)
        if fileName:
            self.opengl_widget.load_obj_file(fileName)
            self.file_display.setText(fileName)
            self.opengl_widget.toggle_vertices()
            self.opengl_widget.toggle_faces()
            self.vertices_display.setText(str(self.opengl_widget.get_vertices_count()))
            self.faces_display.setText(str(self.opengl_widget.get_faces_count()))
            self.shape = ObjectCalculations(fileName)
            # Set the text for the additional statistics
            self.surface_area_display.setText(str(self.shape.surfaceAreaObj))
            self.volume_display.setText(str(self.shape.volume))
            self.compactness_display.setText(str(self.shape.compactnessObj))
            self.rectangularity_display.setText(str(self.shape.rectangularityObj))
            self.diameter_display.setText(str(self.shape.diameterObj))
            self.convexity_display.setText(str(self.shape.convexityObj))
            self.eccentricity_display.setText(str(self.shape.eccentricityObj))
            self.displaySmallerWidgets(fileName)

if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

        
