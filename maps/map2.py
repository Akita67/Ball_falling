import random
import math
from obstacle import Obstacle
from ramp import Ramp
from utils import SCREEN_WIDTH, load_texture


def get_map_layout(seed=None, difficulty='normal'):
    """
    Returns two lists (ramps, obstacles) and a dictionary for the finish line.
    Changes:
      - Seeded RNG for reproducibility (seed=None leaves it random).
      - Difficulty scaling: 'easy' | 'normal' | 'hard'.
      - Non-overlapping bumpers with minimum spacing.
      - Central gutter corridors to maintain flow and avoid softlocks.
      - New sections: Serpentine chicane, Split fork, Tuned bowl, Anti-cheese ceiling lips.
    """
    if seed is not None:
        random.seed(seed)

    # Difficulty knobs
    diff = str(difficulty).lower()
    if diff not in ('easy', 'normal', 'hard'):
        diff = 'normal'

    DIFF = {
        'easy': {
            'bumper_count': 12,
            'bumper_min_dist': 80,
            'tunnel_gap': 180,
            'bowl_hole_width': 80,
            'chicane_width': 140,
            'gutter_width': 120
        },
        'normal': {
            'bumper_count': 18,
            'bumper_min_dist': 65,
            'tunnel_gap': 140,
            'bowl_hole_width': 60,
            'chicane_width': 120,
            'gutter_width': 100
        },
        'hard': {
            'bumper_count': 24,
            'bumper_min_dist': 55,
            'tunnel_gap': 110,
            'bowl_hole_width': 48,
            'chicane_width': 100,
            'gutter_width': 80
        }
    }[diff]

    ramps = []
    obstacles = []

    color_palette = [
        (45, 129, 215), (215, 67, 45), (45, 215, 129),
        (215, 177, 45), (129, 45, 215), (45, 215, 215), (215, 100, 45),
        (70, 70, 70), (230, 230, 230)
    ]

    def rand_color():
        return random.choice(color_palette)

    def place_bumpers_non_overlapping(count, y_min, y_max, min_dist, x_margin=20, gutter_center=None, gutter_width=0):
        """Greedy placement with simple rejection to avoid overlaps and keep a central gutter clear."""
        placed = []
        attempts = 0
        max_attempts = count * 40
        while len(placed) < count and attempts < max_attempts:
            attempts += 1
            x = random.randint(x_margin, int(SCREEN_WIDTH - x_margin))
            y = random.randint(y_min, y_max)
            # Keep a central gutter clear if requested
            if gutter_center is not None and abs(x - gutter_center) < gutter_width / 2:
                continue
            ok = True
            for (px, py, w, h) in placed:
                dx = x - px
                dy = y - py
                if math.hypot(dx, dy) < min_dist:
                    ok = False
                    break
            if ok:
                placed.append((x, y, 25, 25))
        for (x, y, w, h) in placed:
            obstacles.append(Obstacle(x, y, w, h, color=rand_color()))

    # --- SECTION A: Gentle opener with mirrored ramps and side posts ---
    ramps.append(Ramp(0, 200, 120, 210))
    ramps.append(Ramp(SCREEN_WIDTH, 200, SCREEN_WIDTH - 120, 210))
    obstacles.append(Obstacle(160, 400, 20, 110, color=rand_color()))
    obstacles.append(Obstacle(int(SCREEN_WIDTH - 180), 400, 20, 110, color=rand_color()))
    ramps.append(Ramp(0, 600, SCREEN_WIDTH / 2 - 90, 650))
    ramps.append(Ramp(SCREEN_WIDTH, 600, SCREEN_WIDTH / 2 + 90, 650))

    # --- SECTION B: Precision flippers (tighter with difficulty) ---
    y_start = 820
    flipper_rows = 7 if diff == 'easy' else 8 if diff == 'normal' else 9
    spread_x = 40 if diff == 'hard' else 50
    for i in range(flipper_rows):
        flipper_x = random.randint(60, int(SCREEN_WIDTH - 60))
        flipper_y = y_start + i * 120 + random.randint(-28, 28)
        # Diamond flipper cluster
        ramps.append(Ramp(flipper_x, flipper_y, flipper_x + 25, flipper_y + 25))
        ramps.append(Ramp(flipper_x, flipper_y, flipper_x - 25, flipper_y + 25))
        ramps.append(Ramp(flipper_x + 25, flipper_y + 25, flipper_x, flipper_y + 50))
        ramps.append(Ramp(flipper_x - 25, flipper_y + 25, flipper_x, flipper_y + 50))
        # Side mirrors to encourage lane changes
        if random.random() < 0.7:
            mx = min(max(flipper_x + spread_x, 40), SCREEN_WIDTH - 40)
            ramps.append(Ramp(mx, flipper_y + 10, mx + 20, flipper_y + 30))
        if random.random() < 0.7:
            mx = min(max(flipper_x - spread_x, 40), SCREEN_WIDTH - 40)
            ramps.append(Ramp(mx, flipper_y + 10, mx - 20, flipper_y + 30))

    # Non-overlapping bumpers with a central gutter
    gutter_center = SCREEN_WIDTH / 2
    place_bumpers_non_overlapping(
        count=DIFF['bumper_count'],
        y_min= y_start,
        y_max= y_start + 1050,
        min_dist=DIFF['bumper_min_dist'],
        x_margin=24,
        gutter_center=gutter_center,
        gutter_width=DIFF['gutter_width']
    )

    # --- SECTION C: Rhythm platforms (re-tuned angles) ---
    ramps.append(Ramp(110, 1880, SCREEN_WIDTH, 1840))
    ramps.append(Ramp(0, 1990, SCREEN_WIDTH - 80, 2055))
    ramps.append(Ramp(120, 2210, SCREEN_WIDTH, 2195))
    ramps.append(Ramp(0, 2390, SCREEN_WIDTH - 90, 2415))

    # --- SECTION D: Serpentine chicane (forces S-moves) ---
    chicane_y = 2560
    chicane_height = 520
    lane = DIFF['chicane_width']
    left_wall_x = SCREEN_WIDTH / 2 - lane - 40
    right_wall_x = SCREEN_WIDTH / 2 + lane + 40
    segments = 5
    seg_h = chicane_height // segments
    for s in range(segments):
        y0 = chicane_y + s * seg_h
        # Alternate which side pinches in
        if s % 2 == 0:
            # Left pinch
            obstacles.append(Obstacle(left_wall_x, y0, 30, seg_h - 20, color=rand_color()))
            obstacles.append(Obstacle(right_wall_x, y0, 18, seg_h - 20, color=rand_color()))
        else:
            # Right pinch
            obstacles.append(Obstacle(left_wall_x, y0, 18, seg_h - 20, color=rand_color()))
            obstacles.append(Obstacle(right_wall_x, y0, 30, seg_h - 20, color=rand_color()))
    # Entry/exit lips
    obstacles.append(Obstacle(left_wall_x - 22, chicane_y - 10, 22, 14, color=rand_color()))
    obstacles.append(Obstacle(right_wall_x + 2, chicane_y - 10, 22, 14, color=rand_color()))

    # --- SECTION E: Dual tunnels with difficulty-scaled gap ---
    tunnel_y_start = chicane_y + chicane_height + 40
    tunnel_height = 680
    tunnel_width = 84
    gap = DIFF['tunnel_gap']
    left_x = (SCREEN_WIDTH / 2 - gap / 2 - tunnel_width)
    right_x = (SCREEN_WIDTH / 2 + gap / 2)
    obstacles.append(Obstacle(left_x - 20, tunnel_y_start, 20, tunnel_height, color=rand_color()))
    obstacles.append(Obstacle(left_x + tunnel_width, tunnel_y_start, 20, tunnel_height, color=rand_color()))
    obstacles.append(Obstacle(right_x - 20, tunnel_y_start, 20, tunnel_height, color=rand_color()))
    obstacles.append(Obstacle(right_x + tunnel_width, tunnel_y_start, 20, tunnel_height, color=rand_color()))

    # --- SECTION F: Funnel into split fork ---
    funnel_y = tunnel_y_start + tunnel_height + 180
    obstacles.append(Obstacle(SCREEN_WIDTH / 2 - 10, funnel_y, 20, 360, color=rand_color()))
    ramps.append(Ramp(0, funnel_y, SCREEN_WIDTH / 2 - 90, funnel_y + 150))
    ramps.append(Ramp(SCREEN_WIDTH / 2 - 10, funnel_y + 200, 90, funnel_y + 360))
    ramps.append(Ramp(SCREEN_WIDTH, funnel_y, SCREEN_WIDTH / 2 + 90, funnel_y + 150))
    ramps.append(Ramp(SCREEN_WIDTH / 2 + 10, funnel_y + 200, SCREEN_WIDTH - 90, funnel_y + 360))

    # --- SECTION G: Split fork (left = short + technical, right = safe + long) ---
    fork_y = funnel_y + 380
    # Left path: 3-step stairs
    left_x0 = 80
    step_w = (SCREEN_WIDTH / 2) - 120
    step_h = 70
    for i in range(3):
        y0 = fork_y + i * (step_h + 20)
        ramps.append(Ramp(left_x0, y0, left_x0 + step_w - i * 30, y0 + 18 + i * 4))
        # Guard rails to prevent falling off sideways
        obstacles.append(Obstacle(left_x0 - 16, y0 - 6, 16, 24, color=rand_color()))

    # Right path: smooth but pinched
    right_slope_top = fork_y
    ramps.append(Ramp(SCREEN_WIDTH - 60, right_slope_top, SCREEN_WIDTH / 2 + 100, right_slope_top + 240))
    # Pinch posts
    obstacles.append(Obstacle(SCREEN_WIDTH - 120, right_slope_top + 80, 18, 80, color=rand_color()))
    obstacles.append(Obstacle(SCREEN_WIDTH - 170, right_slope_top + 180, 18, 80, color=rand_color()))

    # Rejoin platform
    rejoin_y = fork_y + 320
    ramps.append(Ramp(60, rejoin_y + 60, SCREEN_WIDTH - 60, rejoin_y + 40))

    # --- SECTION H: Peg grid with a protected central gutter ---
    y_start = rejoin_y + 180
    rows = 11 if diff == 'easy' else 12 if diff == 'normal' else 13
    cols = int(SCREEN_WIDTH / 60)
    gutter_w = DIFF['gutter_width']
    for row in range(rows):
        y_pos = y_start + row * 76
        is_offset = row % 2 == 1
        for col in range(cols):
            x_pos = col * 60 + (30 if is_offset else 0)
            if abs(x_pos - SCREEN_WIDTH / 2) < gutter_w / 2:
                continue
            if random.random() > 0.18:
                obstacles.append(Obstacle(x_pos, y_pos, 15, 15, color=rand_color()))

    # --- SECTION I: Convergence bowl (difficulty-scaled hole) ---
    bowl_top_y = y_start + rows * 76 + 120
    bowl_bottom_y = bowl_top_y + 200
    hole_width = DIFF['bowl_hole_width']

    left_hole_x = SCREEN_WIDTH / 2 - hole_width / 2
    points_left = [
        (0, bowl_top_y),
        (60, bowl_top_y + 110),
        (130, bowl_top_y + 180),
        (160, bowl_top_y + 210),
        (left_hole_x, bowl_bottom_y)
    ]
    for i in range(len(points_left) - 1):
        ramps.append(Ramp(points_left[i][0], points_left[i][1], points_left[i + 1][0], points_left[i + 1][1]))

    right_hole_x = SCREEN_WIDTH / 2 + hole_width / 2
    points_right = [
        (SCREEN_WIDTH, bowl_top_y),
        (SCREEN_WIDTH - 60, bowl_top_y + 110),
        (SCREEN_WIDTH - 130, bowl_top_y + 180),
        (SCREEN_WIDTH - 160, bowl_top_y + 210),
        (right_hole_x, bowl_bottom_y)
    ]
    for i in range(len(points_right) - 1):
        ramps.append(Ramp(points_right[i][0], points_right[i][1], points_right[i + 1][0], points_right[i + 1][1]))

    # --- SECTION J: Anti-cheese ceiling lips (block big-air bypass) ---
    lip_y = bowl_top_y - 160
    lip_len = 120
    obstacles.append(Obstacle(0, lip_y, lip_len, 12, color=rand_color()))
    obstacles.append(Obstacle(SCREEN_WIDTH - lip_len, lip_y, lip_len, 12, color=rand_color()))

    # --- Finish line ---
    finish_line_texture = load_texture('finish_line.jpg')
    finish_line_data = {
        'y': bowl_bottom_y + 380,
        'height': 50,
        'texture': finish_line_texture
    }

    return ramps, obstacles, finish_line_data
