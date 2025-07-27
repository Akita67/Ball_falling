import pygame
import random
import numpy
import vidmaker  # <-- Import vidmaker
from ball import Ball
from particle import Particle
from obstacle import Obstacle
from ramp import Ramp
from confetti import Confetti
from utils import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, load_skins
from map import get_map_layout

# --- Recording Flag ---
# Set this to True to record the next race to a video file.
RECORDING = True


def draw_rankings(surface, balls, font, icon_font):
    """Draws the live top 3 ranking on the screen."""
    sorted_balls = sorted(balls, key=lambda b: b.y, reverse=True)

    trophies = {
        0: ("🥇", (255, 215, 0)),
        1: ("🥈", (192, 192, 192)),
        2: ("🥉", (205, 127, 50))
    }

    for i in range(min(3, len(sorted_balls))):
        ball = sorted_balls[i]
        y_pos = 10 + i * 40

        trophy_text, trophy_color = trophies[i]
        trophy_surface = icon_font.render(trophy_text, True, trophy_color)
        surface.blit(trophy_surface, (10, y_pos))

        if ball.skin:
            icon = pygame.transform.scale(ball.skin, (30, 30))
            surface.blit(icon, (50, y_pos))

        name_text = font.render(ball.username, True, WHITE)
        surface.blit(name_text, (90, y_pos + 5))


def game_loop():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Falling Ball Race")
    clock = pygame.time.Clock()

    # --- Fonts ---
    title_font = pygame.font.Font(None, 74)
    font = pygame.font.Font(None, 50)
    small_font = pygame.font.Font(None, 24)
    tiny_font = pygame.font.Font(None, 18)
    ranking_font = pygame.font.Font(None, 28)
    emoji_font_names = ['Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji']
    trophy_font = pygame.font.SysFont(emoji_font_names, 36)

    # --- Video Recorder ---
    video = None
    if RECORDING:
        # Initialize the video recorder if the flag is set
        print("RECORDING ENABLED: The race will be saved to 'race_recording.mp4'")
        video = vidmaker.Video(path="race_recording.mp4", fps=60, resolution=(SCREEN_WIDTH, SCREEN_HEIGHT))
    else:
        print("Recording is disabled.")

    # --- Game State & Timing ---
    game_state = "intro"
    winner = None
    confetti_particles = []
    finish_time = 0
    finish_delay = 500

    # --- Intro Screen ---
    intro_start_time = 0
    intro_duration = 3000
    intro_scroll_x = SCREEN_WIDTH
    player_card_width = 120
    player_card_height = 150

    # --- UI Elements ---
    restart_button_rect = pygame.Rect(SCREEN_WIDTH / 2 - 75, SCREEN_HEIGHT / 2 + 150, 150, 50)
    skip_button_rect = pygame.Rect(SCREEN_WIDTH - 110, SCREEN_HEIGHT - 60, 100, 40)

    def start_race():
        """Initializes or resets all game objects for the race."""
        nonlocal balls, particles, ramps, obstacles, finish_line_props, camera_y, winner, game_state, confetti_particles, ball_skins, intro_start_time, intro_scroll_x, finish_time

        ball_skins = load_skins()
        if not ball_skins:
            print("\n--- No skins loaded. Running with default circles. ---")

        balls = []
        from utils import NUM_BALLS, BALL_RADIUS
        for i in range(NUM_BALLS):
            x_pos = random.randint(BALL_RADIUS, SCREEN_WIDTH - BALL_RADIUS)
            y_pos = random.randint(-SCREEN_HEIGHT, 0)
            skin_info = ball_skins[i % len(ball_skins)] if ball_skins else None
            balls.append(Ball(x_pos, y_pos, skin_info))

        particles = []
        ramps, obstacles, finish_line_props = get_map_layout()
        camera_y = 0.0
        winner = None
        game_state = "intro"
        confetti_particles = []
        finish_time = 0

        intro_start_time = pygame.time.get_ticks()
        intro_scroll_x = SCREEN_WIDTH

    balls, particles, ramps, obstacles, finish_line_props, camera_y, ball_skins = [], [], [], [], {}, 0.0, []
    start_race()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game_state == "finished" and restart_button_rect.collidepoint(event.pos):
                    start_race()
                if game_state == "intro" and skip_button_rect.collidepoint(event.pos):
                    game_state = "race"

        # --- Game Logic ---
        if game_state == "intro":
            elapsed_time = pygame.time.get_ticks() - intro_start_time
            total_width = len(ball_skins) * player_card_width
            start_pos = SCREEN_WIDTH
            end_pos = -total_width

            if elapsed_time < intro_duration:
                progress = elapsed_time / intro_duration
                intro_scroll_x = start_pos + (end_pos - start_pos) * progress
            else:
                game_state = "race"

        elif game_state == "race" or game_state == "finishing":
            for ball in balls:
                ball.update(obstacles, ramps)
            for particle in particles:
                particle.update()
            particles = [p for p in particles if p.lifespan > 0]
            handle_ball_collisions(balls, particles)

            if game_state == "race" and finish_line_props.get('y'):
                for ball in balls:
                    if ball.y + ball.radius > finish_line_props['y']:
                        winner = ball
                        game_state = "finishing"
                        finish_time = pygame.time.get_ticks()
                        break

            if game_state == "finishing" and pygame.time.get_ticks() - finish_time > finish_delay:
                game_state = "finished"
                for _ in range(200):
                    confetti_particles.append(Confetti())

        elif game_state == "finished":
            for p in confetti_particles:
                p.update()

        # --- Camera Control ---
        if (game_state == "race" or game_state == "finishing") and balls:
            leader_ball = max(balls, key=lambda b: b.y)
            target_camera_y = leader_ball.y - SCREEN_HEIGHT / 1.5
            camera_y += (target_camera_y - camera_y) * 0.08

        # --- Drawing ---
        screen.fill(BLACK)

        if game_state == "intro":
            title_text = title_font.render("The Competitors", True, WHITE)
            screen.blit(title_text, title_text.get_rect(center=(SCREEN_WIDTH / 2, 100)))

            for i, skin_info in enumerate(ball_skins):
                card_x = intro_scroll_x + i * player_card_width
                card_y = SCREEN_HEIGHT / 2 - player_card_height / 2
                icon = pygame.transform.scale(skin_info['surface'], (100, 100))
                screen.blit(icon, icon.get_rect(center=(card_x + player_card_width / 2, card_y + 60)))
                name_text = tiny_font.render(skin_info['username'], True, WHITE)
                screen.blit(name_text, name_text.get_rect(center=(card_x + player_card_width / 2, card_y + 130)))

            pygame.draw.rect(screen, (50, 50, 50), skip_button_rect, border_radius=10)
            skip_text = small_font.render("Skip", True, WHITE)
            screen.blit(skip_text, skip_text.get_rect(center=skip_button_rect.center))

        elif game_state == "race" or game_state == "finishing":
            if finish_line_props.get('texture'):
                scaled_texture = pygame.transform.scale(finish_line_props['texture'],
                                                        (SCREEN_WIDTH, finish_line_props['height']))
                screen.blit(scaled_texture, (0, finish_line_props['y'] - camera_y))
            for ramp in ramps:
                ramp.draw(screen, camera_y)
            for obstacle in obstacles:
                obstacle.draw(screen, camera_y)
            for particle in particles:
                particle.draw(screen, camera_y)
            for ball in balls:
                ball.draw(screen, camera_y)

            draw_rankings(screen, balls, ranking_font, trophy_font)

        elif game_state == "finished" and winner:
            if finish_line_props.get('texture'):
                scaled_texture = pygame.transform.scale(finish_line_props['texture'],
                                                        (SCREEN_WIDTH, finish_line_props['height']))
                screen.blit(scaled_texture, (0, finish_line_props['y'] - camera_y))
            for ramp in ramps:
                ramp.draw(screen, camera_y)
            for obstacle in obstacles:
                obstacle.draw(screen, camera_y)
            for particle in particles:
                particle.draw(screen, camera_y)
            for ball in balls:
                ball.draw(screen, camera_y)

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

        # --- Add frame to video ---
        if RECORDING and video:
            # Capture the current screen frame
            frame = pygame.surfarray.array3d(screen)
            # Transpose the frame from (width, height, 3) to (height, width, 3) for vidmaker
            transposed_frame = numpy.transpose(frame, (1, 0, 2))
            # Add the frame to the video
            video.update(transposed_frame, inverted=True)

        clock.tick(60)

    # --- Finalize and close video ---
    if RECORDING and video:
        print("Saving video... this may take a moment.")
        video.close()
        print("Video saved as 'race_recording.mp4'")

    pygame.quit()


def handle_ball_collisions(balls, particles):
    for i in range(len(balls)):
        for j in range(i + 1, len(balls)):
            ball1 = balls[i]
            ball2 = balls[j]
            ball1.collide_with_ball(ball2, particles)


if __name__ == "__main__":
    game_loop()
