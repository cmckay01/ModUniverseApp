import numpy as np
from utilities import runge_kutta, AU

class SolarSystemBody:
    def __init__(self, solar_system, mass, radius, position, velocity):
        self.solar_system = solar_system
        self.mass = mass
        self.radius = radius  # Used for collision detection
        self.position = np.array(position, dtype=np.float64)
        self.velocity = np.array(velocity, dtype=np.float64)
        self.history = []  # Store historical positions
        self.show_trail = True
        
    def draw(self, ax):
        if self.show_trail and len(self.history) > 1:
            ax.plot(*np.array(self.history).T, linestyle='-', marker='', color=self.color)
        ax.scatter(*self.position, s=self.radius / AU * 100000, marker='o', color=self.color)

    def move(self, dt):
        runge_kutta(self, dt, self.solar_system)
        self.history.append(self.position.copy())
