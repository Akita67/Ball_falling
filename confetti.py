import pygame
import random
from utils import SCREEN_WIDTH, SCREEN_HEIGHT, CONFETTI_COLORS

class Confetti:
    """Represents a single piece of celebratory confetti."""
    def __init__(self):
        # Start at a random position across the top of the screen.
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(-SCREEN_HEIGHT, 0)
        self.vx = random.uniform(-1, 1) # Slight horizontal drift
        self.vy = random.uniform(3, 7)  # Falling speed
        self.color = random.choice(CONFETTI_COLORS)
        self.width = random.randint(5, 10)
        self.height = random.randint(10, 15)
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        """Update confetti position."""
        self.x += self.vx
        self.y += self.vy
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface):
        """Draw the confetti piece on the screen."""
        pygame.draw.rect(surface, self.color, self.rect)
