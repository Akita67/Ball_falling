import pygame
import random
from utils import SPARKLE_COLORS

class Particle:
    """Represents a single sparkle particle for collision effects."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.lifespan = random.randint(20, 40)
        self.color = random.choice(SPARKLE_COLORS)
        self.radius = random.randint(2, 5)

    def update(self):
        """Update particle's position and decrease its lifespan."""
        self.x += self.vx
        self.y += self.vy
        self.lifespan -= 1

    def draw(self, surface, camera_y):
        """Draw the particle, adjusted for camera position."""
        current_radius = int(self.radius * (self.lifespan / 40))
        if current_radius > 0:
            pos = (int(self.x), int(self.y - camera_y))
            pygame.draw.circle(surface, self.color, pos, current_radius)
