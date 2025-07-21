import pygame
import random
from ball import Ball
from particle import Particle
from obstacle import Obstacle
from ramp import Ramp
from confetti import Confetti
from utils import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, load_skins
from map import get_map_layout


def game_loop():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Falling Ball Race")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 50)
    small_font = pygame.font.Font(None, 36)

    game_state = "race"
    winner = None
    confetti_particles = []
    restart_button_rect = pygame.Rect(SCREEN_WIDTH / 2 - 75, SCREEN_HEIGHT / 2 + 150, 150, 50)

    def start_race():
        nonlocal balls, particles, ramps, obstacles, finish_line_props, camera_y, winner, game_state, confetti_particles

        ball_skins = load_skins()
        if not ball_skins:
            print("\n--- No skins loaded. Running with default circles. ---")
        else:
            random.shuffle(ball_skins)

        balls = []
        from utils import NUM_BALLS, BALL_RADIUS
        for i in range(NUM_BALLS):
            x_pos = random.randint(BALL_RADIUS, SCREEN_WIDTH - BALL_RADIUS)
            y_pos = random.randint(-SCREEN_HEIGHT, 0)
            skin_info = ball_skins[i % len(ball_skins)] if ball_skins else None
            balls.append(Ball(x_pos, y_pos, skin_info))

        particles = []
        # Get the finish line properties dictionary from the map layout
        ramps, obstacles, finish_line_props = get_map_layout()
        camera_y = 0.0
        winner = None
        game_state = "race"
        confetti_particles = []

    balls, particles, ramps, obstacles, finish_line_props, camera_y = [], [], [], [], {}, 0.0
    start_race()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game_state == "finished" and restart_button_rect.collidepoint(event.pos):
                    start_race()

        if game_state == "race":
            for ball in balls:
                ball.update(obstacles, ramps)
            for particle in particles:
                particle.update()
            particles = [p for p in particles if p.lifespan > 0]
            handle_ball_collisions(balls, particles)

            # Check for a winner using the finish line's y-coordinate
            for ball in balls:
                if ball.y + ball.radius > finish_line_props['y']:
                    winner = ball
                    game_state = "finished"
                    for _ in range(200):
                        confetti_particles.append(Confetti())
                    break

        elif game_state == "finished":
            for p in confetti_particles:
                p.update()

        if game_state == "race" and balls:
            leader_ball = max(balls, key=lambda b: b.y)
            target_camera_y = leader_ball.y - SCREEN_HEIGHT / 1.5
            camera_y += (target_camera_y - camera_y) * 0.08

        screen.fill(BLACK)

        # Draw the finish line using its properties
        if finish_line_props.get('texture'):
            scaled_texture = pygame.transform.scale(
                finish_line_props['texture'],
                (SCREEN_WIDTH, finish_line_props['height'])
            )
            screen.blit(scaled_texture, (0, finish_line_props['y'] - camera_y))

        for ramp in ramps:
            ramp.draw(screen, camera_y)
        for obstacle in obstacles:
            obstacle.draw(screen, camera_y)
        for particle in particles:
            particle.draw(screen, camera_y)
        for ball in balls:
            ball.draw(screen, camera_y)

        if game_state == "finished" and winner:
            for p in confetti_particles:
                p.draw(screen)

            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            winner_text = font.render("WINNER!", True, WHITE)
            screen.blit(winner_text, winner_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 150)))

            username_text = small_font.render(winner.username, True, (255, 215, 0))
            screen.blit(username_text, username_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 100)))

            if winner.skin:
                winner_img = pygame.transform.scale(winner.skin, (200, 200))
                screen.blit(winner_img, winner_img.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 20)))

            pygame.draw.rect(screen, (0, 150, 0), restart_button_rect, border_radius=10)
            restart_text = font.render("Restart", True, WHITE)
            screen.blit(restart_text, restart_text.get_rect(center=restart_button_rect.center))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


def handle_ball_collisions(balls, particles):
    for i in range(len(balls)):
        for j in range(i + 1, len(balls)):
            ball1 = balls[i]
            ball2 = balls[j]
            ball1.collide_with_ball(ball2, particles)


if __name__ == "__main__":
    game_loop()
