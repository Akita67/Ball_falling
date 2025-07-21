import pygame
import random
import math
from utils import GRAVITY, FRICTION, BALL_RADIUS, SCREEN_WIDTH, WHITE
from particle import Particle


class Ball:
    """Represents a single falling ball in the race."""

    def __init__(self, x, y, skin_info):
        self.x = x
        self.y = y
        self.radius = BALL_RADIUS
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-5, 0)
        self.mass = 1.0

        # Unpack skin info
        if skin_info:
            self.skin = skin_info['surface']
            self.username = skin_info['username']
        else:
            self.skin = None
            self.username = f"Ball {random.randint(100, 999)}"

        if self.skin:
            self.mask = pygame.mask.from_surface(self.skin)
        else:
            self.mask = pygame.mask.Mask((self.radius * 2, self.radius * 2), True)

    def update(self, obstacles, ramps):
        self.vy += GRAVITY
        self.x += self.vx
        self.y += self.vy

        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx *= -FRICTION
        elif self.x + self.radius > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.radius
            self.vx *= -FRICTION

        for obstacle in obstacles:
            obstacle.collide_with_ball(self)

        for ramp in ramps:
            ramp.collide_with_ball(self)

    def collide_with_ball(self, other_ball, particles):
        dx = other_ball.x - self.x
        dy = other_ball.y - self.y
        distance = math.hypot(dx, dy)

        if distance < self.radius + other_ball.radius and distance > 0:
            for _ in range(random.randint(5, 15)):
                particles.append(Particle((self.x + other_ball.x) / 2, (self.y + other_ball.y) / 2))

            nx, ny = dx / distance, dy / distance
            tx, ty = -ny, nx

            dpTan1 = self.vx * tx + self.vy * ty
            dpTan2 = other_ball.vx * tx + other_ball.vy * ty
            dpNorm1 = self.vx * nx + self.vy * ny
            dpNorm2 = other_ball.vx * nx + other_ball.vy * ny

            m1 = (dpNorm1 * (self.mass - other_ball.mass) + 2 * other_ball.mass * dpNorm2) / (
                        self.mass + other_ball.mass)
            m2 = (dpNorm2 * (other_ball.mass - self.mass) + 2 * self.mass * dpNorm1) / (self.mass + other_ball.mass)

            self.vx = (tx * dpTan1 + nx * m1) * FRICTION
            self.vy = (ty * dpTan1 + ny * m1) * FRICTION
            other_ball.vx = (tx * dpTan2 + nx * m2) * FRICTION
            other_ball.vy = (ty * dpTan2 + ny * m2) * FRICTION

            overlap = 0.5 * (self.radius + other_ball.radius - distance + 1)
            self.x -= overlap * nx
            self.y -= overlap * ny
            other_ball.x += overlap * nx
            other_ball.y += overlap * ny

    def draw(self, surface, camera_y):
        center_pos = (int(self.x), int(self.y - camera_y))
        pygame.draw.circle(surface, WHITE, center_pos, self.radius + 1)

        if self.skin:
            draw_pos = (self.x - self.radius, self.y - self.radius - camera_y)
            surface.blit(self.skin, draw_pos)
        else:
            pygame.draw.circle(surface, (200, 200, 200), center_pos, self.radius)
