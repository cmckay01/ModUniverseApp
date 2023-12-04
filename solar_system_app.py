from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QMessageBox, QFormLayout, QLineEdit, QDialogButtonBox, QDialog, QLabel, QComboBox, QRadioButton
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
        self.quiz_progress = 0
        self.initializeQuizQuestions()


    def initUI(self):
        self.setWindowTitle('Solar System Simulation')
        self.setGeometry(100, 100, 800, 600)
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout(self.central_widget)
        
        self.canvas = FigureCanvas(Figure())
        self.ax = self.canvas.figure.add_subplot(111, projection='3d')
        layout.addWidget(self.canvas)

        # Create menu bar items
        menuBar = self.menuBar()
        controlMenu = menuBar.addMenu('Controls')
        quizMenu = menuBar.addMenu('Quiz')

        # Add actions to the control menu
        controlMenu.addAction('Start Simulation', self.startSimulation)
        controlMenu.addAction('Toggle Orbit Trails', self.toggleOrbitTrails)
        controlMenu.addAction('List Bodies Info', self.listBodiesInfo)
        controlMenu.addAction('Add New Body', self.showNewBodyDialog)

        # Add action to the quiz menu
        quizMenu.addAction('Start Quiz', self.showQuiz)

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

    def initializeQuizQuestions(self):
        self.quiz_questions = [
            # Include all the quiz questions here with explanations
            {"question": "What is the force that keeps planets in orbit around the sun?", 
             "options": ["Gravity", "Magnetism", "Electrostatic force"], 
             "answer": "Gravity",
             "explanation": "Gravity is the force that keeps planets in orbit. It's the attractive force between two masses."},

            {"question": "If a satellite orbits closer to the Earth, how does its orbital speed compare to a satellite farther away?",
             "options": ["Faster", "Slower", "The same", "Cannot be determined"],
             "answer": "Faster",
             "explanation": "According to Kepler's third law, orbital speed increases as the orbital radius decreases."},
            
            {"question": "How does the gravitational force between two objects change if the distance between them doubles?",
             "options": ["Increases four times", "Decreases four times", "Increases two times", "Decreases two times"],
             "answer": "Decreases four times",
             "explanation": "Gravitational force is inversely proportional to the square of the distance. Doubling the distance decreases the force by a factor of four."},

            {"question": "What is the minimum velocity needed for an object to maintain a stable orbit around the Sun at 1 AU?",
            "options": ["29.78 km/s", "24.13 km/s", "42.1 km/s", "33.2 km/s"],
            "answer": "29.78 km/s",
            "explanation": "The minimum velocity for a stable orbit at 1 AU (the distance of Earth from the Sun) is about 29.78 km/s. This is calculated using the formula v = √(GM/r), where G is the gravitational constant, M is the mass of the Sun, and r is the radius of the orbit."},

             # New questions
            {"question": "What would happen to Earth's orbit if the Sun's mass suddenly doubled?",
             "options": ["The orbit would remain the same", "The orbit would become more elliptical", "The Earth would move closer to the Sun", "The Earth would move farther from the Sun"],
             "answer": "The Earth would move closer to the Sun",
             "explanation": "Doubling the Sun's mass would increase the gravitational force, pulling Earth closer and possibly leading to a more elliptical orbit."},

            {"question": "What is the escape velocity from Earth's surface?",
             "options": ["7.9 km/s", "11.2 km/s", "9.8 m/s^2", "5.5 km/s"],
             "answer": "11.2 km/s",
             "explanation": "Escape velocity is the speed needed to break free from a planet's gravitational pull. For Earth, it's approximately 11.2 km/s."},

            {"question": "How does the orbital period of a planet change with respect to its semi-major axis length?",
             "options": ["Increases linearly", "Decreases linearly", "Increases with the square of the semi-major axis length", "Increases with the cube root of the semi-major axis length"],
             "answer": "Increases with the cube root of the semi-major axis length",
             "explanation": "According to Kepler's third law, the square of a planet's orbital period is proportional to the cube of the semi-major axis of its orbit."},

            {"question": "If a new planet was discovered at 2 AU from the Sun, how would its year compare to Earth's?",
             "options": ["About the same as Earth's", "Twice as long as Earth's", "Half as long as Earth's", "Approximately 2.8 times longer than Earth's"],
             "answer": "Approximately 2.8 times longer than Earth's",
             "explanation": "Using Kepler's third law, a planet at 2 AU would have an orbital period √2³ = 2.8 times longer than Earth's year."},

            {"question": "What is the significance of the Lagrange points in a two-body system?",
             "options": ["Points where gravitational forces are balanced", "Points where escape velocity is zero", "Points where orbital speed is highest", "Points where gravitational forces are strongest"],
             "answer": "Points where gravitational forces are balanced",
             "explanation": "Lagrange points are positions where the gravitational pull of two large bodies precisely equals the centripetal force required to orbit with them."},

            {"question": "Calculate the orbital speed of a satellite at a height of 300 km above Earth's surface. (Earth's radius = 6371 km, Earth's mass = 5.97e24 kg)",
             "options": ["7.8 km/s", "8.1 km/s", "7.4 km/s", "8.5 km/s"],
             "answer": "7.8 km/s",
             "explanation": "Orbital speed v = √(GM/(R+h)), where R is Earth's radius, h is satellite's height. Plugging in the values gives v ≈ 7.8 km/s."},

            {"question": "A planet orbits a star twice the mass of the Sun at the same distance as Earth from the Sun. What is its orbital period compared to Earth's?",
             "options": ["Same as Earth's", "Twice Earth's", "Half of Earth's", "Four times Earth's"],
             "answer": "Same as Earth's",
             "explanation": "Orbital period depends on the semi-major axis, not the star's mass. So, it remains the same as Earth's."},

            {"question": "What would be the gravitational force between two 1 kg masses 1 meter apart?",
             "options": ["6.67e-11 N", "6.67e-10 N", "1 N", "0 N"],
             "answer": "6.67e-11 N",
             "explanation": "Using Newton's law of universal gravitation, F = Gm1m2/r², where G is 6.67e-11 Nm²/kg²."},

        ]
    
        self.quiz_progress = 0

    def showQuiz(self):
        if self.quiz_progress >= len(self.quiz_questions):
            QMessageBox.information(self, "Quiz", "You have completed all the questions!")
            choice = QMessageBox.question(self, "Restart Quiz?", "Do you want to restart the quiz?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if choice == QMessageBox.Yes:
                self.quiz_progress = 0
            return

        self.current_question = self.quiz_questions[self.quiz_progress]
        dialog = QDialog(self)
        dialog.setWindowTitle("Quiz")

        layout = QVBoxLayout(dialog)

        questionLabel = QLabel(self.current_question["question"], dialog)
        layout.addWidget(questionLabel)

        self.selected_answer = None
        for option in self.current_question["options"]:
            rb = QRadioButton(option, dialog)
            rb.toggled.connect(lambda checked, opt=option: self.onAnswerSelected(checked, opt))
            layout.addWidget(rb)

        submitButton = QPushButton("Submit", dialog)
        submitButton.clicked.connect(lambda: self.checkAnswer(dialog, submitButton))
        layout.addWidget(submitButton)

        dialog.setLayout(layout)
        dialog.exec_()

    def checkAnswer(self, dialog, submitButton):
        correct = self.selected_answer == self.current_question["answer"]
        message = "Correct!" if correct else f"Incorrect! The correct answer was '{self.current_question['answer']}'.\n\nExplanation: {self.current_question['explanation']}"
        QMessageBox.information(self, "Quiz", message)
        submitButton.setText("Next Question" if self.quiz_progress < len(self.quiz_questions) - 1 else "Finish Quiz")
        submitButton.clicked.disconnect()
        submitButton.clicked.connect(lambda: self.nextOrFinishQuiz(dialog))

    def nextOrFinishQuiz(self, dialog):
        self.quiz_progress += 1
        dialog.accept()
        self.showQuiz()

    def onAnswerSelected(self, checked, option):
        if checked:
            self.selected_answer = option

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





