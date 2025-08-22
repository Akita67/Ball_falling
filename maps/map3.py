import random
from obstacle import Obstacle
from ramp import Ramp
from utils import SCREEN_WIDTH, load_texture


def get_map_layout():
    """
    Returns two lists (ramps, obstacles) and a dictionary for the finish line.
    This version keeps a single dead-end vertical lane in the slanted maze.
    """
    ramps = []
    obstacles = []

    color_palette = [
        (45, 129, 215), (215, 67, 45), (45, 215, 129),
        (215, 177, 45), (129, 45, 215), (45, 215, 215), (215, 100, 45)
    ]

    # --- Sections 1-2 ---
    ramps.append(Ramp(0, 200, 120, 210))
    ramps.append(Ramp(SCREEN_WIDTH, 200, SCREEN_WIDTH - 120, 210))
    obstacles.append(Obstacle(160, 400, 20, 100, color=random.choice(color_palette)))
    obstacles.append(Obstacle(SCREEN_WIDTH - 180, 400, 20, 100, color=random.choice(color_palette)))
    ramps.append(Ramp(0, 600, SCREEN_WIDTH / 2 - 80, 650))
    ramps.append(Ramp(SCREEN_WIDTH, 600, SCREEN_WIDTH / 2 + 80, 650))

    y_start = 800
    for i in range(8):
        flipper_x = random.randint(50, int(SCREEN_WIDTH) - 50)
        flipper_y = y_start + i * 120 + random.randint(-30, 30)
        ramps.append(Ramp(flipper_x, flipper_y, flipper_x + 25, flipper_y + 25))
        ramps.append(Ramp(flipper_x, flipper_y, flipper_x - 25, flipper_y + 25))
        ramps.append(Ramp(flipper_x + 25, flipper_y + 25, flipper_x, flipper_y + 50))
        ramps.append(Ramp(flipper_x - 25, flipper_y + 25, flipper_x, flipper_y + 50))

    for i in range(15):
        bumper_x = random.randint(20, int(SCREEN_WIDTH) - 20)
        bumper_y = y_start + random.randint(0, 1000)
        obstacles.append(Obstacle(bumper_x, bumper_y, 25, 25, color=random.choice(color_palette)))

    ramps.append(Ramp(100, 1880, SCREEN_WIDTH, 1840))
    ramps.append(Ramp(0, 1990, SCREEN_WIDTH - 100, 2050))
    ramps.append(Ramp(100, 2210, SCREEN_WIDTH, 2190))
    ramps.append(Ramp(0, 2390, SCREEN_WIDTH - 100, 2410))

    tunnel_y_start = 2650
    tunnel_height = 700
    tunnel_width = 80
    gap = 150
    left_x = (SCREEN_WIDTH / 2 - gap / 2 - tunnel_width)
    right_x = (SCREEN_WIDTH / 2 + gap / 2)

    obstacles.append(Obstacle(left_x - 20, tunnel_y_start, 20, tunnel_height, color=random.choice(color_palette)))
    obstacles.append(Obstacle(left_x + tunnel_width, tunnel_y_start, 20, tunnel_height, color=random.choice(color_palette)))
    obstacles.append(Obstacle(right_x - 20, tunnel_y_start, 20, tunnel_height, color=random.choice(color_palette)))
    obstacles.append(Obstacle(right_x + tunnel_width, tunnel_y_start, 20, tunnel_height, color=random.choice(color_palette)))

    funnel_y = 3500
    obstacles.append(Obstacle(SCREEN_WIDTH / 2 - 10, funnel_y, 20, 400, color=random.choice(color_palette)))
    ramps.append(Ramp(0, funnel_y, SCREEN_WIDTH / 2 - 80, funnel_y + 150))
    ramps.append(Ramp(SCREEN_WIDTH / 2 - 10, funnel_y + 200, 80, funnel_y + 350))
    ramps.append(Ramp(SCREEN_WIDTH, funnel_y, SCREEN_WIDTH / 2 + 80, funnel_y + 150))
    ramps.append(Ramp(SCREEN_WIDTH / 2 + 10, funnel_y + 200, SCREEN_WIDTH - 80, funnel_y + 350))

    y_start = 4000
    for row in range(12):
        y_pos = y_start + row * 80
        is_offset = row % 2 == 1
        for col in range(int(SCREEN_WIDTH / 60)):
            x_pos = col * 60 + (30 if is_offset else 0)
            if random.random() > 0.15:
                obstacles.append(Obstacle(x_pos, y_pos, 15, 15, color=random.choice(color_palette)))

    # --- Convergence Bowl ---
    bowl_top_y = 5200
    bowl_bottom_y = 5400
    hole_width = 60

    left_hole_x = SCREEN_WIDTH / 2 - hole_width / 2
    points_left = [
        (0, bowl_top_y),
        (50, bowl_top_y + 100),
        (120, bowl_top_y + 170),
        (150, bowl_top_y + 200),
        (left_hole_x, bowl_bottom_y)
    ]
    for i in range(len(points_left) - 1):
        ramps.append(Ramp(points_left[i][0], points_left[i][1], points_left[i + 1][0], points_left[i + 1][1]))

    right_hole_x = SCREEN_WIDTH / 2 + hole_width / 2
    points_right = [
        (SCREEN_WIDTH, bowl_top_y),
        (SCREEN_WIDTH - 50, bowl_top_y + 100),
        (SCREEN_WIDTH - 120, bowl_top_y + 170),
        (SCREEN_WIDTH - 150, bowl_top_y + 200),
        (right_hole_x, bowl_bottom_y)
    ]
    for i in range(len(points_right) - 1):
        ramps.append(Ramp(points_right[i][0], points_right[i][1], points_right[i + 1][0], points_right[i + 1][1]))

    # --- Slanted Maze with single dead-end column ---
    maze_top_y = 5600
    rows = 9
    cols = 5
    row_h = 140
    wall_thickness = 14
    cell_w = SCREEN_WIDTH / cols

    dead_end_col = random.randint(0, cols - 1)  # one unlucky column

    for r in range(rows):
        y0 = maze_top_y + r * row_h

        # Slanted dividers
        for c in range(cols):
            x0 = c * cell_w
            if r % 2 == 0:
                ramps.append(Ramp(x0 + 10, y0 + row_h - 22, x0 + cell_w - 10, y0 + 22))
            else:
                ramps.append(Ramp(x0 + 10, y0 + 22, x0 + cell_w - 10, y0 + row_h - 22))

        # Dead-end column walls (block fully)
        if r == 0:
            # top of dead-end
            x0 = dead_end_col * cell_w
            obstacles.append(Obstacle(x0, y0, cell_w, rows * row_h, color=random.choice(color_palette)))

    # Maze exit funnel
    maze_bottom_y = maze_top_y + rows * row_h
    ramps.append(Ramp(0, maze_bottom_y, SCREEN_WIDTH / 2 - 100, maze_bottom_y + 120))
    ramps.append(Ramp(SCREEN_WIDTH, maze_bottom_y, SCREEN_WIDTH / 2 + 100, maze_bottom_y + 120))

    # --- Finish Line ---
    finish_line_texture = load_texture('finish_line.jpg')
    finish_line_data = {
        'y': maze_bottom_y + 180,
        'height': 50,
        'texture': finish_line_texture
    }

    return ramps, obstacles, finish_line_data
