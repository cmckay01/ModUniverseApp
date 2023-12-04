from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QMessageBox, QFormLayout, QLineEdit, QDialogButtonBox, QDialog, QLabel, QComboBox
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from solar_system import SolarSystem
from solar_system_body import SolarSystemBody
from utilities import AU, G
import regex as re

#contant:
sun_mass=1.989e+30

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

        #self.stableOrbitButton = QPushButton('Stable Orbit Calculator', self)
        #self.stableOrbitButton.clicked.connect(self.showStableOrbitDialog)
        #controlsLayout.addWidget(self.stableOrbitButton)

        self.addBodyButton = QPushButton('Add New Body', self)
        self.addBodyButton.clicked.connect(self.showNewBodyDialog)
        controlsLayout.addWidget(self.addBodyButton)

        self.initSolarSystem()
    
    def showNewBodyDialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Body")

        layout = QFormLayout(dialog)

        # Input fields for mass
        massEdit = QLineEdit(dialog)
        massUnitCombo = QComboBox(dialog)
        massUnitCombo.addItems(["kg", "Earth masses"])

        # Input field for distance from Sun
        distanceEdit = QLineEdit(dialog)
        distanceUnitCombo = QComboBox(dialog)
        distanceUnitCombo.addItems(["m", "AU"])

        # Input field for velocity
        velocityEdit = QLineEdit(dialog)

        layout.addRow("Mass:", massEdit)
        layout.addRow("Mass Unit:", massUnitCombo)
        layout.addRow("Distance from Sun:", distanceEdit)
        layout.addRow("Distance Unit:", distanceUnitCombo)
        layout.addRow("Velocity (vx, vy, vz) in m/s:", velocityEdit)

        # Info button
        infoButton = QPushButton("Info", dialog)
        infoButton.clicked.connect(self.showInfo)
        layout.addWidget(infoButton)

        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
        buttons.accepted.connect(lambda: self.calculate_and_add_body(
            massEdit.text(), 
            massUnitCombo.currentText(), 
            distanceEdit.text(), 
            distanceUnitCombo.currentText(), 
            velocityEdit.text())
        )
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)
        dialog.exec_()

    def calculate_and_add_body(self, mass, massUnit, distance_str, distanceUnit, velocity_str):
        # Parse distance and calculate suggested velocity
        try:
            # Convert distance from AU to meters if necessary
            distance_components = self.parse_vector(distance_str)
            if distanceUnit == "AU":
                distance_components = tuple(d * AU for d in distance_components)
            if len(distance_components) != 3:
                raise ValueError("Invalid distance components")
            distance = np.linalg.norm(distance_components)  # Actual distance from the sun
        except ValueError as e:
            QMessageBox.warning(self, "Input Error", f"Please enter valid numerical values for distance. Error: {e}")
            return

        suggested_velocity = (G * 1.989e+30 / distance)**0.5  # Sun's mass

        # Show suggested velocity and limitations disclaimer
        reply = QMessageBox.question(self, "Suggested Velocity",
            f"Suggested Velocity for a stable orbit: {suggested_velocity:.2f} m/s\n\n"
            "Note: This is an approximation assuming a circular orbit around the sun. "
            "Other celestial bodies might influence the actual stability of the orbit.\n\n"
            "Do you want to add the body with this velocity?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # Assuming initial position in the XY plane for simplicity
            self.addNewBody(mass, massUnit, f"{distance_components[0]},{distance_components[1]},0", f"0,0,{suggested_velocity}")
    

    def showInfo(self):
        infoDialog = QDialog(self)
        infoDialog.setWindowTitle("Input Format and Examples")

        infoText = """
        <p><b>Mass:</b> Enter the mass in kilograms. Use scientific notation if needed (e.g., '5.97e24' or '5.97*10^24' for Earth's mass or as as a multiple of Earth's mass (e.g., '1' for Earth's mass).</p>
        <p><b>Position:</b> Enter the position as x, y, z coordinates in meters. 
        Separate values with commas (e.g., '-1.496e11, 0, 0' for Earth's position or for AU: '-1 AU, 0 AU, 0 AU' for Earth's position from the Sun.)</p>
        <p><b>Velocity:</b> Enter the velocity as vx, vy, vz components in meters per second. 
        Use commas to separate values (e.g., '0, 29780, 0' for Earth's velocity).</p>
        """

        infoLayout = QVBoxLayout()
        infoLabel = QLabel(infoText, infoDialog)
        infoLayout.addWidget(infoLabel)

        closeButton = QPushButton("Close", infoDialog)
        closeButton.clicked.connect(infoDialog.close)
        infoLayout.addWidget(closeButton)

        infoDialog.setLayout(infoLayout)
        infoDialog.exec_()

    def addNewBody(self, mass, massUnit, position_str, velocity_str):
        # Convert mass based on selected unit
        mass = float(mass)
        if massUnit == "Earth masses":
            mass *= 5.97e24  # Earth's mass

        # Parse position
        position = self.parse_vector(position_str)

        # Parse velocity
        velocity = self.parse_vector(velocity_str)

        # Create a new SolarSystemBody and add it to the simulation
        new_body = SolarSystemBody(self.solarSystem, mass, 1e6, position, velocity)  # Set a default radius
        new_body.color = 'green'  # Default color
        self.solarSystem.add_body(new_body)
        self.updatePlot()

    def parse_vector(self, vector_str):
        # Strip 'AU' if present and extract numbers
        vector_str = vector_str.replace('AU', '').replace('au', '')
        vector_components = re.findall(r"[-+]?\d*\.\d+|\d+", vector_str)
        return tuple(map(float, vector_components))
    
    def parse_scientific_notation(self, s):
        """Parse a string in scientific notation."""
        # Regex to identify parts of scientific notation
        match = re.search(r'([\d\.]+)\*?10\^?(\-?\d+)', s)
        if match:
            base, exponent = match.groups()
            return float(base) * (10 ** float(exponent))
        else:
            return float(s)  # Fallback to normal float conversion
    
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
        self.ax.clear()
        self.ax.set_xlim([-1e12, 1e12])  # Set fixed limits for x-axis
        self.ax.set_ylim([-1e12, 1e12])  # Set fixed limits for y-axis
        self.ax.set_zlim([-1e12, 1e12])  # Set fixed limits for z-axis
        self.ax.clear()
        for body in self.solarSystem.bodies:
            body.draw(self.ax)
        self.canvas.draw()





