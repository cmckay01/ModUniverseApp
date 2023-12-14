from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QKeySequence
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from solar_system import SolarSystem
from solar_system_body import SolarSystemBody
import math
from utilities import AU, G
import regex as re
import sys

#contant:
sun_mass=1.989e+30

class SolarSystemApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.plot_bounds = None
        self.solarSystem = SolarSystem()  # Instantiate SolarSystem object 
        self.initUI()
        self.quiz_progress = 0


    def initUI(self):
        self.setWindowTitle('Solar System Simulation')
        self.setGeometry(100, 100, 800, 600)
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Main layout for the central widget
        mainLayout = QVBoxLayout(self.central_widget)

        # Initialize the canvas for Matplotlib
        self.canvas = FigureCanvas(Figure())
        self.ax = self.canvas.figure.add_subplot(111, projection='3d')
        mainLayout.addWidget(self.canvas)

        # Create menu bar items
        menuBar = self.menuBar()
        controlMenu = menuBar.addMenu('Controls')
        quizMenu = menuBar.addMenu('Quiz')

        # Add actions to the control menu
        controlMenu.addAction('Start Simulation', self.startSimulation)
        controlMenu.addAction('Toggle Orbit Trails', self.toggleOrbitTrails)
        #controlMenu.addAction('Reset Orbit Trails', self.clearOrbitTrails)
        #controlMenu.addAction('List Bodies Info', self.listBodiesInfo)
        #controlMenu.addAction('Add New Body', self.showNewBodyDialog)
        #controlMenu.addAction('Adjust Body Mass', self.showMassAdjustmentDialog)
        controlMenu.addAction('Reset Simulation', self.resetSimulation)

        # Add action to the quiz menu
        #quizMenu.addAction('Start Quiz', self.showQuiz)

        # A layout for sliders and their labels
        self.slidersLayout = QVBoxLayout()
        mainLayout.addLayout(self.slidersLayout)

        # Initialize solar system and mass sliders (w/ scale factor)
        self.initSolarSystem()
    
    def initSolarSystem(self):
        self.solarSystem = SolarSystem()

        # Sun
        self.sun = SolarSystemBody(self.solarSystem, mass=1.989e+30, radius=696340000, position=(0, 0, 0), velocity=(0, 0, 0))
        self.sun.color = 'yellow'
        self.solarSystem.add_body(self.sun)

        # Earth
        earth_velocity = (0, np.sqrt(G * self.sun.mass / AU), 0)
        earth = SolarSystemBody(self.solarSystem, mass=5.97e+24, radius=6371000, position=(-AU, 0, 0), velocity=earth_velocity)
        earth.color = 'blue'
        self.solarSystem.add_body(earth)

        # Mars
        mars_distance = 1.5 * AU
        mars_velocity = (0, np.sqrt(G * self.sun.mass / mars_distance), 0)
        mars = SolarSystemBody(self.solarSystem, mass=6.39e+23, radius=3389500, position=(-mars_distance, 0, 0), velocity=mars_velocity)
        mars.color = 'red'
        self.solarSystem.add_body(mars)

        # Jupiter
        jupiter_distance = 5.2 * AU
        jupiter_velocity = (0, np.sqrt(G * self.sun.mass / jupiter_distance), 0)
        jupiter = SolarSystemBody(self.solarSystem, mass=1.898e+27, radius=69911000, position=(-jupiter_distance, 0, 0), velocity=jupiter_velocity)
        jupiter.color = 'orange'
        self.solarSystem.add_body(jupiter)

    def startSimulation(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateSimulation)
        self.timer.start(50)  # 50 milliseconds
    
    def resetSimulation(self):
        # Reset the simulation
        self.initSolarSystem()  # Reinitialize the solar system
        self.updatePlot()

    def updateSimulation(self):
        dt = 3600 * 24 * 7 # One day in seconds
        self.solarSystem.calculate_all_body_interactions(dt)
        self.solarSystem.update_all(dt)
        self.updatePlot()
        
        collision_info, collision_position = self.solarSystem.check_collisions()
        if collision_info is not None:
            self.timer.stop()
            body1, body2 = collision_info
            QMessageBox.information(self, "Collision Alert", f"Collision detected between bodies {body1} and {body2} at position {collision_position}.")

    def toggleOrbitTrails(self):
        for body in self.solarSystem.bodies:
            body.show_trail = not body.show_trail
        self.updatePlot()

    def updatePlot(self):
        # Store current axis limits if they exist
        if self.ax.has_data():
            current_xlim = self.ax.get_xlim()
            current_ylim = self.ax.get_ylim()
            current_zlim = self.ax.get_zlim()
        else:
            current_xlim = current_ylim = current_zlim = None

        self.ax.clear()
        
        # Calculate bounds when trails are visible or bounds are not set
        if any(body.show_trail for body in self.solarSystem.bodies) or self.plot_bounds is None:
            x_min, x_max, y_min, y_max, z_min, z_max = self.calculatePlotBounds()
            self.plot_bounds = (x_min, x_max, y_min, y_max, z_min, z_max)
        else:
            x_min, x_max, y_min, y_max, z_min, z_max = self.plot_bounds

        # Set the plot limits
        self.ax.set_xlim(x_min, x_max)
        self.ax.set_ylim(y_min, y_max)
        self.ax.set_zlim(z_min, z_max)

        # Draw the bodies
        for body in self.solarSystem.bodies:
            body.draw(self.ax)

        self.canvas.draw()

        # Reapply the stored axis limits
        if current_xlim is not None:
            self.ax.set_xlim(current_xlim)
            self.ax.set_ylim(current_ylim)
            self.ax.set_zlim(current_zlim)

        self.canvas.draw()

    def calculatePlotBounds(self):
        positions = []
        for body in self.solarSystem.bodies:
            positions.extend(body.history)  # Include orbit trail positions
            positions.append(body.position)  # Include current position

        if not positions:
            return -1, 1, -1, 1, -1, 1  # Default bounds if no bodies

        positions = np.array(positions)
        x_min, x_max = positions[:,0].min(), positions[:,0].max()
        y_min, y_max = positions[:,1].min(), positions[:,1].max()
        z_min, z_max = positions[:,2].min(), positions[:,2].max()

        # Add some padding to the bounds
        padding = max(x_max - x_min, y_max - y_min, z_max - z_min) * 0.9
        return x_min-padding, x_max+padding, y_min-padding, y_max+padding, z_min-padding, z_max+padding

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SolarSystemApp()
    ex.show()
    sys.exit(app.exec_())



