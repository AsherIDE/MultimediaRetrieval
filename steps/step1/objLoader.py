import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtOpenGL import QGLWidget
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

############################################################################################
# Load object file
############################################################################################
def load_obj(filename):
    vertices = []
    faces = []
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('v '):
                vertices.append(list(map(float, line.strip().split()[1:])))
            elif line.startswith('f '):
                face = [int(val.split('/')[0]) - 1 for val in line.strip().split()[1:]]
                faces.append(face)
    return np.array(vertices, dtype=np.float32), np.array(faces, dtype=np.int32)

############################################################################################
# OpenGL widget
############################################################################################
class OpenGLWidget(QGLWidget):
    def __init__(self, parent=None):
        super(OpenGLWidget, self).__init__(parent)
        self.vertices = None
        self.faces = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateGL)
        self.timer.start(48)  # 16 is near 60 fps 
        #voor de camera
        self.camera_pos = np.array([0.0, 0.0, -5.0])  # X, Y, Z position
        self.mouse_last_pos = None
        self.is_right_button_pressed = False  # Initialize the flag here 
        self.is_left_button_pressed = False #Left button standard false 
        # Object rotation angles
        self.rotation_x = 0
        self.rotation_y = 0

    def initializeGL(self):
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

    # adding color to the object
    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Apply camera translation before rendering the object
        glLoadIdentity()  # Reset transformations
        glTranslatef(self.camera_pos[0], self.camera_pos[1], self.camera_pos[2]) 

        # Apply object rotation based on mouse input
        glRotatef(self.rotation_x, 1, 0, 0)  # Rotate around X-axis
        glRotatef(self.rotation_y, 0, 1, 0)  # Rotate around Y-axis


        if self.vertices is not None and self.faces is not None:
            self.draw_model()
    # rendering the object
    def draw_model(self):
        glBegin(GL_TRIANGLES)
        for face in self.faces:
            for vertex in face:
                glColor3fv([0.8, 0.3, 0.3])  # Red color
                glVertex3fv(self.vertices[vertex])
        glEnd()

    # updating object
    def updateGL(self):
        glRotatef(1, 3, 10, 1)  # Rotate the object
        self.update()

    # loading .obj file from file directory
    def load_obj_file(self, filename):
        self.vertices, self.faces = load_obj(filename)

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
        zoom_sensitivity = 0.05  # Adjust sensitivity as needed
        delta = event.angleDelta().y()  # Get the scroll amount
    
        if delta > 0:
            self.camera_pos[2] += zoom_sensitivity  # Zoom out
        else:
            self.camera_pos[2] -= zoom_sensitivity  # Zoom in
    
        self.update()  # Update the view
        
############################################################################################
# Window (in which OpenGL widget exists)
############################################################################################
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Object testing')
        self.setGeometry(100, 100, 800, 600)
        
        self.opengl_widget = OpenGLWidget(self)
        
        # select .obj file button
        self.button = QPushButton('Open OBJ File', self)
        self.button.clicked.connect(self.open_file_dialog)
        
        # widgets in window
        layout = QVBoxLayout()
        layout.addWidget(self.opengl_widget)
        layout.addWidget(self.button)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
    
    def open_file_dialog(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open OBJ File", "", "OBJ Files (*.obj);;All Files (*)", options=options)
        if fileName:
            self.opengl_widget.load_obj_file(fileName)



# execution of the program
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())