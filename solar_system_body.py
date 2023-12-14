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
        self.visual_radius = self.calculate_visual_radius()
        self.marker = None

    def calculate_visual_radius(self):
        # Simple example: scale radius based on cube root of mass
        return (self.mass / 5.97e24)**(1/3) * 1e7  # Earth's mass as reference
    
    def draw(self, ax):
        if self.show_trail and len(self.history) > 1:
            ax.plot(*np.array(self.history).T, linestyle='-', marker='', color=self.color)

        # Calculate zoom level factor
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        zlim = ax.get_zlim()
        max_range = max(xlim[1] - xlim[0], ylim[1] - ylim[0], zlim[1] - zlim[0])
        zoom_factor = max_range / (2 * AU)  # Assuming initial zoom level is set around 2 AU

        # Base visual size (adjust as needed)
        base_visual_size = (self.visual_radius / AU * 1000000)
        
        # Scale visual size based on zoom factor
        scaled_visual_size = base_visual_size / zoom_factor 

        ax.scatter(*self.position, s=scaled_visual_size, marker='o', color=self.color)

        # Check if marker already exists
        if self.marker is not None:
            # Update position and size if marker exists
            self.marker.set_offsets(self.position[:2])  # assuming 3D positions
        else:
            # Create a new marker
            visual_size = (self.visual_radius / AU * 100000)
            self.marker = ax.scatter(*self.position, s=visual_size, marker='o', color=self.color)

    def update_visual_size(self, ax):
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        zlim = ax.get_zlim()
        max_range = max(xlim[1] - xlim[0], ylim[1] - ylim[0], zlim[1] - zlim[0])
        zoom_factor = max_range / (2 * AU)  # Assuming initial zoom level is set around 2 AU

        base_visual_size = (self.visual_radius / AU * 1000000)
        scaled_visual_size = base_visual_size / zoom_factor 

        if self.marker is not None:
            self.marker.set_sizes([scaled_visual_size])

    def move(self, dt):
        runge_kutta(self, dt, self.solar_system)
        self.history.append(self.position.copy())
