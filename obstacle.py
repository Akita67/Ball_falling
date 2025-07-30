import pygame
import math
from utils import OBSTACLE_COLOR, FRICTION


class Obstacle:
    """Represents a static rectangular obstacle with a specific color."""

    def __init__(self, x, y, width, height, color=OBSTACLE_COLOR):
        self.rect = pygame.Rect(x, y, width, height)
        # Each obstacle now has its own color attribute.
        self.color = color

    def draw(self, surface, camera_y):
        """Draw the obstacle with its unique color, adjusted for camera position."""
        draw_rect = self.rect.copy()
        draw_rect.y -= camera_y

        # --- Discrete Neon Glow ---
        # Create a rectangle for the glow, slightly larger than the obstacle
        glow_rect_inflated = self.rect.inflate(8, 8)
        glow_rect_inflated.y -= camera_y

        # Create a temporary surface for the glow effect that supports transparency
        glow_surface = pygame.Surface(glow_rect_inflated.size, pygame.SRCALPHA)

        # Use the obstacle's color for the glow, but with a low alpha for a discrete effect
        glow_color = (*self.color, 40)  # Low alpha for subtlety

        # Draw the glowing rectangle on the temporary surface
        pygame.draw.rect(glow_surface, glow_color, glow_surface.get_rect(), border_radius=7)

        # Blit the glow surface to the screen, centered with the obstacle
        surface.blit(glow_surface, glow_rect_inflated.topleft)

        # Draw the main obstacle rectangle on top of the glow
        pygame.draw.rect(surface, self.color, draw_rect, border_radius=5)


    def collide_with_ball(self, ball):
        """Check and resolve collision with a ball."""
        closest_x = max(self.rect.left, min(ball.x, self.rect.right))
        closest_y = max(self.rect.top, min(ball.y, self.rect.bottom))

        distance_x = ball.x - closest_x
        distance_y = ball.y - closest_y
        distance_squared = (distance_x ** 2) + (distance_y ** 2)

        if distance_squared < (ball.radius ** 2) and distance_squared > 0:
            distance = math.sqrt(distance_squared)
            overlap = ball.radius - distance

            normal_x = distance_x / distance
            normal_y = distance_y / distance

            ball.x += normal_x * overlap
            ball.y += normal_y * overlap

            dot_product = ball.vx * normal_x + ball.vy * normal_y

            ball.vx -= 2 * dot_product * normal_x
            ball.vy -= 2 * dot_product * normal_y

            ball.vx *= FRICTION
            ball.vy *= FRICTION