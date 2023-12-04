import numpy as np
from scipy.constants import G

# Constants
G = G  # Gravitational constant from scipy.constants
AU = 1.496e+11  # Astronomical unit in meters


def runge_kutta(body, dt, solar_system):
        def calculate_gravitational_acceleration(position):
            acceleration = np.zeros_like(position)
            for other_body in solar_system.bodies:
                if other_body != body:
                    distance_vector = other_body.position - position
                    distance_mag = np.linalg.norm(distance_vector)
                    force_mag = G * body.mass * other_body.mass / distance_mag**2
                    force_direction = distance_vector / distance_mag
                    acceleration += force_direction * force_mag / body.mass
            return acceleration

        k1v = calculate_gravitational_acceleration(body.position) * dt
        k1p = body.velocity * dt
        k2v = calculate_gravitational_acceleration(body.position + 0.5 * k1p) * dt
        k2p = (body.velocity + 0.5 * k1v) * dt
        k3v = calculate_gravitational_acceleration(body.position + 0.5 * k2p) * dt
        k3p = (body.velocity + 0.5 * k2v) * dt
        k4v = calculate_gravitational_acceleration(body.position + k3p) * dt
        k4p = (body.velocity + k3v) * dt

        body.position += (k1p + 2 * k2p + 2 * k3p + k4p) / 6
        body.velocity += (k1v + 2 * k2v + 2 * k3v + k4v) / 6
