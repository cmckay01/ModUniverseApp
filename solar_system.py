from solar_system_body import SolarSystemBody
import numpy as np

class SolarSystem:
    def __init__(self):
        self.bodies = []

    def add_body(self, body):
        self.bodies.append(body)

    def update_all(self, dt):
        for body in self.bodies:
            body.move(dt)

    def calculate_all_body_interactions(self, dt):
        for body in self.bodies:
            body.move(dt)


    def check_collisions(self):
        for i, body in enumerate(self.bodies):
            for j, other_body in enumerate(self.bodies):
                if i != j:
                    distance = np.linalg.norm(body.position - other_body.position)
                    if distance < (body.radius + other_body.radius):
                        print(f"Collision detected between body {i} and body {j}")
                        print(f"Distance: {distance}, Combined Radii: {body.radius + other_body.radius}")
                        print(f"Positions: {body.position}, {other_body.position}")
                        return (i, j), body.position
        return None, None