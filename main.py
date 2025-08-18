import pygame
import random
import numpy
import vidmaker  # <-- Import vidmaker
from ball import Ball
from particle import Particle
from obstacle import Obstacle
from ramp import Ramp
from confetti import Confetti
from utils import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, load_skins, load_texture
from map import get_map_layout
import subprocess

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
        y_pos = 50 + i * 40

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
    countdown_font = pygame.font.Font(None, 200) # Font for the countdown
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

    # --- Dynamic Background ---
    background_img = load_texture('Nebula Aqua-Pink.png')
    stars_imgs = [
        load_texture('Stars Small_1.png'),
        load_texture('Stars Small_2.png'),
        load_texture('Stars-Big_1_1_PC.png'),
        load_texture('Stars-Big_1_2_PC.png')
    ]
    bg_y = 0
    stars_y = [0, 0, 0, 0]
    star_speeds = [0.1, 0.2, 0.35, 0.5]


    # --- Game State & Timing ---
    game_state = "intro"
    winner = None
    confetti_particles = []
    finish_time = 0
    finish_delay = 500

    # --- Intro Screen & Countdown---
    intro_start_time = 0
    intro_duration = 3000
    intro_scroll_x = SCREEN_WIDTH
    player_card_width = 120
    player_card_height = 150
    countdown_start_time = 0
    countdown_duration = 3000

    # --- Load Intro Music ---
    pygame.mixer.init()
    pygame.mixer.music.load("assets/intro_music2.mp3")  # Adjust path as needed
    pygame.mixer.music.set_volume(0.5)  # Optional: set volume
    pygame.mixer.music.play(1)  # -1 means loop indefinitely

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
            # Balls now spawn in a tighter cluster at the top of the screen
            y_pos = random.randint(-SCREEN_HEIGHT // 4, -BALL_RADIUS * 2)
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
                    game_state = "countdown"
                    countdown_start_time = pygame.time.get_ticks()

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
                game_state = "countdown"
                countdown_start_time = pygame.time.get_ticks()

        elif game_state == "countdown":
            elapsed_time = pygame.time.get_ticks() - countdown_start_time
            if elapsed_time >= countdown_duration:
                game_state = "race"
                pygame.mixer.music.stop()

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
        elif game_state == "countdown": # Keep camera still during countdown
             leader_ball = max(balls, key=lambda b: b.y)
             target_camera_y = leader_ball.y - SCREEN_HEIGHT / 1.5
             camera_y = target_camera_y

        # --- Drawing ---
        screen.fill(BLACK)

        # Draw Dynamic Background
        if background_img:
            bg_y = -camera_y * 0.1  # Slower scroll for the main background
            # Tiling the background
            screen.blit(background_img, (0, bg_y % background_img.get_height() - background_img.get_height()))
            screen.blit(background_img, (0, bg_y % background_img.get_height()))

        for i, stars_img in enumerate(stars_imgs):
            if stars_img:
                stars_y[i] = -camera_y * star_speeds[i]
                # Tiling the star layers
                screen.blit(stars_img, (0, stars_y[i] % stars_img.get_height() - stars_img.get_height()))
                screen.blit(stars_img, (0, stars_y[i] % stars_img.get_height()))


        if game_state == "intro":
            title_text = title_font.render("The Competitors", True, WHITE)
            screen.blit(title_text, title_text.get_rect(center=(SCREEN_WIDTH / 2, 100)))

            for i, skin_info in enumerate(ball_skins):
                card_x = intro_scroll_x + i * player_card_width
                card_y = SCREEN_HEIGHT / 2 - player_card_height / 2
                if(i%2==0):
                    card_y = (SCREEN_HEIGHT / 2 - player_card_height / 2)*(1.2)
                if(i%3==0):
                    card_y = (SCREEN_HEIGHT / 2 - player_card_height / 2) * (1.4)
                if (i%4==0):
                    card_y = (SCREEN_HEIGHT / 2 - player_card_height / 2) * (1.6)
                if (i % 5 == 0):
                    card_y = (SCREEN_HEIGHT / 2 - player_card_height / 2) * (1.8)

                icon = pygame.transform.scale(skin_info['surface'], (100, 100))
                screen.blit(icon, icon.get_rect(center=(card_x + player_card_width / 2, card_y + 60)))
                name_text = tiny_font.render(skin_info['username'], True, WHITE)
                screen.blit(name_text, name_text.get_rect(center=(card_x + player_card_width / 2, card_y + 130)))

            pygame.draw.rect(screen, (50, 50, 50), skip_button_rect, border_radius=10)
            skip_text = small_font.render("Skip", True, WHITE)
            screen.blit(skip_text, skip_text.get_rect(center=skip_button_rect.center))

        elif game_state == "countdown":
            # Draw everything in a static position
            if finish_line_props.get('texture'):
                scaled_texture = pygame.transform.scale(finish_line_props['texture'],
                                                        (SCREEN_WIDTH, finish_line_props['height']))
                screen.blit(scaled_texture, (0, finish_line_props['y'] - camera_y))
            for ramp in ramps:
                ramp.draw(screen, camera_y)
            for obstacle in obstacles:
                obstacle.draw(screen, camera_y)
            for ball in balls:
                ball.draw(screen, camera_y)

            # Draw countdown text
            elapsed = pygame.time.get_ticks() - countdown_start_time
            countdown_num = 3 - (elapsed // 1000)
            if countdown_num > 0:
                text = countdown_font.render(str(countdown_num), True, WHITE)
                text_rect = text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
                screen.blit(text, text_rect)

                # Draw the "Follow to join" text
                follow_text = font.render("Follow if you want to join!", True, WHITE)
                follow_rect = follow_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 6 + 100))
                screen.blit(follow_text, follow_rect)


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
                winner_img = pygame.transform.smoothscale(winner.skin, (200, 200))
                screen.blit(winner_img, winner_img.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 20)))

            elapsed_time = pygame.time.get_ticks()


            if elapsed_time - (finish_delay + finish_time) > 15000:
                break

            # pygame.draw.rect(screen, (0, 150, 0), restart_button_rect, border_radius=10)
            # restart_text = font.render("Restart", True, WHITE)
            # screen.blit(restart_text, restart_text.get_rect(center=restart_button_rect.center))

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
        video.export(verbose=True)
        # Merge intro MP3 with recorded MP4
        print("Merging intro music with video...")
        subprocess.run([
            "ffmpeg",
            "-y",
            "-i", "race_recording.mp4",  # Video input
            "-i", "assets/intro_music2.mp3",  # Audio input
            "-c:v", "copy",  # Copy video stream without re-encoding
            "-c:a", "aac",  # Encode audio to AAC
            "-shortest",  # Trim to the shortest stream (video or audio)
            "final_output.mp4"
        ])

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