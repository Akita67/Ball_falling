import random
from obstacle import Obstacle
from ramp import Ramp
from utils import SCREEN_WIDTH, load_texture


def get_map_layout():
    """
    Returns two lists (ramps, obstacles) and a dictionary for the finish line.
    """
    ramps = []
    obstacles = []

    color_palette = [
        (45, 129, 215), (215, 67, 45), (45, 215, 129),
        (215, 177, 45), (129, 45, 215), (45, 215, 215), (215, 100, 45)
    ]

    # --- Sections 1-4 (Same as before) ---
    ramps.append(Ramp(0, 200, 120, 210))
    ramps.append(Ramp(SCREEN_WIDTH, 200, SCREEN_WIDTH - 120, 210))
    obstacles.append(Obstacle(160, 400, 20, 100, color=random.choice(color_palette)))
    obstacles.append(Obstacle(SCREEN_WIDTH - 180, 400, 20, 100, color=random.choice(color_palette)))
    ramps.append(Ramp(0, 600, SCREEN_WIDTH / 2 - 40, 610))
    ramps.append(Ramp(SCREEN_WIDTH, 600, SCREEN_WIDTH / 2 + 40, 610))

    y_start = 800
    for row in range(12):
        y_pos = y_start + row * 80
        is_offset = row % 2 == 1
        for col in range(int(SCREEN_WIDTH / 60)):
            x_pos = col * 60 + (30 if is_offset else 0)
            if random.random() > 0.15:
                obstacles.append(Obstacle(x_pos, y_pos, 15, 15, color=random.choice(color_palette)))

    ramps.append(Ramp(100, 1810, SCREEN_WIDTH, 1790))
    ramps.append(Ramp(0, 1990, SCREEN_WIDTH - 100, 2010))
    ramps.append(Ramp(100, 2210, SCREEN_WIDTH, 2190))
    ramps.append(Ramp(0, 2390, SCREEN_WIDTH - 100, 2410))

    tunnel_y_start = 2650
    tunnel_height = 700
    tunnel_width = 80
    gap = 150
    left_x = (SCREEN_WIDTH / 2 - gap / 2 - tunnel_width)
    right_x = (SCREEN_WIDTH / 2 + gap / 2)
    obstacles.append(Obstacle(left_x - 20, tunnel_y_start, 20, tunnel_height, color=random.choice(color_palette)))
    obstacles.append(
        Obstacle(left_x + tunnel_width, tunnel_y_start, 20, tunnel_height, color=random.choice(color_palette)))
    obstacles.append(Obstacle(right_x - 20, tunnel_y_start, 20, tunnel_height, color=random.choice(color_palette)))
    obstacles.append(
        Obstacle(right_x + tunnel_width, tunnel_y_start, 20, tunnel_height, color=random.choice(color_palette)))

    # --- Section 5: The Final Drop & Finish Line ---
    ramps.append(Ramp(0, 3450, SCREEN_WIDTH / 3, 3465))
    ramps.append(Ramp(SCREEN_WIDTH, 3450, SCREEN_WIDTH * 2 / 3, 3465))
    ramps.append(Ramp(SCREEN_WIDTH / 2 - 50, 3650, SCREEN_WIDTH / 2 + 50, 3660))

    # Load the finish line texture and store its properties in a dictionary
    finish_line_texture = load_texture('finish_line.png') # Make sure this is in your 'assets' folder
    finish_line_data = {
        'y': 4500,
        'height': 50,
        'texture': finish_line_texture
    }

    return ramps, obstacles, finish_line_data
