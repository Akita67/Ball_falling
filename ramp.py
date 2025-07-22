import pygame
import math
from utils import OBSTACLE_COLOR, FRICTION


class Ramp:
    """Represents a static inclined line segment (a ramp)."""

    def __init__(self, x1, y1, x2, y2, thickness=5):
        self.p1 = pygame.math.Vector2(x1, y1)
        self.p2 = pygame.math.Vector2(x2, y2)
        self.thickness = thickness
        self.color = OBSTACLE_COLOR

    def draw(self, surface, camera_y):
        """Draw the ramp, adjusted for camera position."""
        p1_screen = (self.p1.x, self.p1.y - camera_y)
        p2_screen = (self.p2.x, self.p2.y - camera_y)
        pygame.draw.line(surface, self.color, p1_screen, p2_screen, self.thickness)

    def collide_with_ball(self, ball):
        """Check and resolve collision with a ball."""
        ball_pos = pygame.math.Vector2(ball.x, ball.y)
        line_vec = self.p2 - self.p1

        # Handle case of zero-length ramp to avoid division by zero
        if line_vec.length_squared() == 0:
            return

        # Find the projection of the ball's position onto the line
        p1_to_ball = ball_pos - self.p1
        t = p1_to_ball.dot(line_vec) / line_vec.length_squared()

        # Clamp t to be on the line segment [0, 1]
        t = max(0, min(1, t))

        # Find the closest point on the line segment to the ball
        closest_point = self.p1 + t * line_vec

        # Vector from closest point to ball center
        vec_to_ball = ball_pos - closest_point
        dist_sq = vec_to_ball.length_squared()

        # If the distance is less than the ball's radius, there's a collision
        if dist_sq < ball.radius ** 2 and dist_sq > 0:
            dist = math.sqrt(dist_sq)
            overlap = ball.radius - dist

            # The collision normal is the direction from the closest point to the ball
            normal = vec_to_ball / dist

            # Reposition the ball to be just outside the ramp
            ball.x += normal.x * overlap
            ball.y += normal.y * overlap

            # --- Bounce Physics ---
            ball_vel = pygame.math.Vector2(ball.vx, ball.vy)

            # Calculate the dot product of the velocity and the normal
            dot_product = ball_vel.dot(normal)

            # Reflect the velocity vector
            new_vel = ball_vel - 2 * dot_product * normal

            # Apply friction
            ball.vx = new_vel.x * FRICTION * 1.15
            ball.vy = new_vel.y * FRICTION
