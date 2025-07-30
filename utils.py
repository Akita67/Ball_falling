import pygame
import os

# --- Screen and Display ---
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 800

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
OBSTACLE_COLOR = (255, 255, 255)
SPARKLE_COLORS = [(255, 255, 0), (255, 200, 0), (255, 150, 0), (255, 255, 255)]
CONFETTI_COLORS = [
    (255, 87, 87), (255, 195, 0), (87, 255, 87),
    (87, 169, 255), (185, 87, 255), (255, 255, 255)
]

# --- Game Physics and Parameters ---
GRAVITY = 0.13
FRICTION = 0.85
BALL_RADIUS = 15
NUM_BALLS = len(os.listdir('skins'))


def load_texture(filename, folder='assets'):
    """Loads a single texture image from the assets folder."""
    path = os.path.join(folder, filename)
    if not os.path.exists(path):
        print(f"Error: Texture file not found at '{path}'")
        return None
    try:
        texture = pygame.image.load(path).convert_alpha()
        return texture
    except pygame.error as e:
        print(f"Could not load texture '{filename}': {e}")
        return None


def load_skins(folder_path='skins'):
    """Loads all supported image types from a specified folder and crops them."""
    skins = []
    if not os.path.exists(folder_path):
        print(f"Warning: The '{folder_path}' folder was not found.")
        return skins

    supported_formats = ('.png', '.jpg', '.jpeg')
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(supported_formats):
            try:
                path = os.path.join(folder_path, filename)
                image = pygame.image.load(path)
                username = os.path.splitext(filename)[0]  # Get username from filename

                if filename.lower().endswith('.png'):
                    image = image.convert_alpha()
                else:
                    image = image.convert()

                scaled_image = pygame.transform.scale(image, (BALL_RADIUS * 2, BALL_RADIUS * 2))

                circle_surface = pygame.Surface((BALL_RADIUS * 2, BALL_RADIUS * 2), pygame.SRCALPHA)
                pygame.draw.circle(circle_surface, (255, 255, 255), (BALL_RADIUS, BALL_RADIUS), BALL_RADIUS)
                circle_surface.blit(scaled_image, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                # Store the surface and the username together
                skins.append({'surface': circle_surface, 'username': username})

            except pygame.error as e:
                print(f"Could not load image '{filename}': {e}")

    return skins
