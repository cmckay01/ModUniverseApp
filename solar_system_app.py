from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QMessageBox
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from solar_system import SolarSystem
from solar_system_body import SolarSystemBody
from utilities import AU, G

class SolarSystemApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Solar System Simulation')
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)

        self.canvas = FigureCanvas(Figure())
        self.ax = self.canvas.figure.add_subplot(111, projection='3d')
        layout.addWidget(self.canvas)

        self.startButton = QPushButton('Start Simulation', self)
        self.startButton.clicked.connect(self.startSimulation)
        controlsLayout = QHBoxLayout()
        controlsLayout.addWidget(self.startButton)
        layout.addLayout(controlsLayout)

        self.toggleTrailButton = QPushButton('Toggle Orbit Trails', self)
        self.toggleTrailButton.clicked.connect(self.toggleOrbitTrails)
        controlsLayout.addWidget(self.toggleTrailButton)

        self.listBodiesButton = QPushButton('List Bodies Info', self)
        self.listBodiesButton.clicked.connect(self.listBodiesInfo)
        controlsLayout.addWidget(self.listBodiesButton)

        self.initSolarSystem()
    
    def listBodiesInfo(self):
        info = []
        for i, body in enumerate(self.solarSystem.bodies):
            body_name = f"Body {i}"
            info.append(f"{body_name}: Position: {body.position}, Mass: {body.mass}")
        info_str = "\n".join(info)
        QMessageBox.information(self, "Bodies Information", info_str)

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

        """ # Add a rogue planet or black hole
        rogue_mass = 1.989e+30 * 1000  # Mass 1000 times that of the Sun
        rogue_distance = 3 * AU  # Position it some distance away
        rogue_velocity = (0, -np.sqrt(G * self.sun.mass / rogue_distance) / 2, 0)  # Giving it an initial velocity
        rogue_planet = SolarSystemBody(self.solarSystem, mass=rogue_mass, radius=696340000, position=(rogue_distance, 0, 0), velocity=rogue_velocity)
        rogue_planet.color = 'black'  # Color it black to represent a black hole
        self.solarSystem.add_body(rogue_planet) """


        """ # Black hole parameters
        black_hole_mass = 1.989e+30 * 1000  # Mass 1000 times that of the Sun
        black_hole_distance = 220 * AU  # A greater distance
        black_hole_velocity = (0, np.sqrt(G * self.sun.mass / black_hole_distance) / 3, 0)  # A slower initial velocity

        # Add the black hole
        black_hole = SolarSystemBody(self.solarSystem, mass=black_hole_mass, radius=696340000, position=(black_hole_distance, 0, 0), velocity=black_hole_velocity)
        black_hole.color = 'black'
        self.solarSystem.add_body(black_hole) """

    def startSimulation(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateSimulation)
        self.timer.start(50)  # 50 milliseconds

    def updateSimulation(self):
        dt = 3600 * 24 # One day in seconds
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
        self.ax.clear()
        for body in self.solarSystem.bodies:
            body.draw(self.ax)
        self.canvas.draw()
