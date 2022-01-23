import math
import pygame
from Point import Point, Force, Spring
from line_intersect import is_line_intersect

# --- Constants for Colors etc. ---
C_BG     = (255, 255, 255)
C_CANVAS = (255, 255, 255)
C_LINE   = (0, 0, 0)
C_START  = (0, 255, 0)
C_GOAL   = (255, 0, 0)
C_PATH   = (0, 0, 255)
C_TEXT   = (0, 0, 0)

"""
win = pygame.display.set_mode((1200, 800))
clock = pygame.time.Clock()
FPS = 60
"""
# --- Display init ---
win_x, win_y = 850, 600
win = pygame.display.set_mode((win_x, win_y))
pygame.display.set_caption("Maze Solver")
win.fill(C_BG)

# --- Clock init ---
clock = pygame.time.Clock()
FPS = 60

# --- Text ---
pygame.font.init()
font = pygame.font.SysFont('arial', 15, True)
textes = [
        "P - Node tool",
        "F - Static node tool",
        "S - Spring tool",
        "D - Cut-and-Delete tool",
        "M - Move tool",
        "B - Force tool",
        "SPACE - Toggle gravity"
        ]

# --- Canvas ---
canvas_x = int(2*win_x/3) + 1   # 2/3 of win
canvas_y = win_y - 20 + 1     # Add one to both to make room for an additional ending line 
offset_x = 0
offset_y = 0
canvas = pygame.Surface((canvas_x, canvas_y))
canvas.fill(C_CANVAS)
pygame.draw.rect(canvas, C_LINE, (0, 0, canvas_x, canvas_y), 1)

rest_length = 20
constant = 0.1

points  = set()
springs = set()

n_points_x = 10
n_points_y = 10
points_matrix = [[0 for _ in range(n_points_y)] for _ in range(n_points_x)]

# --- Functions ---
def create_start_mesh(n_points_x, n_points_y):
    """ Create a start mesh of size n_points_x * n_points_y """
    for x in range(n_points_x):
        for y in range(n_points_y):
            if y == 0:
                points_matrix[x][y] = Point(x*rest_length + 100, y*rest_length + 100, static=True)
            else:
                points_matrix[x][y] = Point(x*rest_length + 100, y*rest_length + 100)
    for row in points_matrix:
        for p in row:
            points.add(p)
    for x in range(n_points_x):
        for y in range(n_points_y):
            if x != 0:
                spring = Spring(points_matrix[x][y], points_matrix[x-1][y], constant, rest_length)
                springs.add(spring)
            if y != 0:
                spring = Spring(points_matrix[x][y], points_matrix[x][y-1], constant, rest_length)
                springs.add(spring)

def render_text(win, x, y, spacing=10):
    """ Renders the text specified in textes """
    for text in textes:
        text_surface = font.render(text, False, C_TEXT)
        win.blit(text_surface, (x, y))
        y += text_surface.get_height() + spacing


def redrawWindow(win):
    canvas.fill(C_CANVAS)
    pygame.draw.rect(canvas, C_LINE, (0, 0, canvas_x, canvas_y), 1)
    for s in springs:
        s.draw(canvas)
    for p in points:
        p.draw(canvas)
    win.blit(canvas, (offset_x, offset_y))
    
    render_text(win, canvas_x+20, 50)
    pygame.display.update()

def pos_collide_circle(point, mid, radius):
    """ Check if a position (e.g. from the mouse) collides with any circle (i.e. a node/point) """
    x = point[0]
    y = point[1]
    if mid[0] - radius <= x <= mid[0] + radius:
        if mid[1] - radius <= y <= mid[1] + radius:
            return True
    return False


# --- Main loop ---

has_clicked = False
temp_points = []
to_move = None
UPDATE = False
mode = 'p'
create_start_mesh(n_points_x, n_points_y)

RUNNING = True
while RUNNING:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            RUNNING = False
        if event.type == pygame.MOUSEBUTTONUP:
            if mode == 'd':
                temp_points.clear()
                has_clicked = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if mode == 'b':
                for p in points:
                    p.add_force(Force(10, 0))
            elif mode == 'm':
                for p in points:
                    if pos_collide_circle(pos, (p.x, p.y), p.radius):
                        to_move = p
                        break
                    else:
                        to_move = None
            elif mode == 'p':
                points.add(Point(pos[0], pos[1]))
            elif mode == 'f':
                points.add(Point(pos[0], pos[1], static=True))
            elif mode == 's':
                for p in points:
                    if pos_collide_circle(pos, (p.x, p.y), p.radius):
                        if not p in temp_points:
                            temp_points.append(p)
                            if has_clicked:
                                spring = Spring(temp_points[0], temp_points[1], constant, rest_length)
                                springs.add(spring)
                                temp_points = []
                                has_clicked = False
                            else:
                                has_clicked = True
                            break
            
        elif event.type == pygame.KEYDOWN:
            temp_points = []
            has_clicked = False
            if to_move:
                to_move.static = False
            if event.key == pygame.K_p:
                mode = 'p'
            elif event.key == pygame.K_s:
                mode = 's'
            elif event.key == pygame.K_f:
                mode = 'f'
            elif event.key == pygame.K_SPACE:
                UPDATE = not UPDATE
            elif event.key == pygame.K_d:
                mode = 'd'
            elif event.key == pygame.K_b:
                mode = 'b'
            elif event.key == pygame.K_m:
                mode = 'm'

    pressed = pygame.mouse.get_pressed()
    if pressed[0]:
        pos = pygame.mouse.get_pos()
        if mode == 'm':
            if to_move:
                # to_move.static = True
                to_move.x = pos[0]
                to_move.y = pos[1]
        elif mode == 'd':
            removed_point = None
            springs_to_remove = set()
            # See what point is clicked on
            for p in points:
                if pos_collide_circle(pos, (p.x, p.y), p.radius):
                    removed_point = p
                    break
            # Remove point and any attached springs
            if removed_point:
                points.remove(removed_point)
                for s in springs:
                    if (p == s.p1 or p == s.p2):
                        springs_to_remove.add(s)
            # Check if "cutting" with mouse just started
            if not has_clicked:
                    temp_points.append(Point(pos[0], pos[1]))
                    has_clicked = True
            # Else cut all springs between the mouse's current and previous position
            else:
                for s in springs:
                    if is_line_intersect(temp_points[0], Point(pos[0], pos[1]), s.p1, s.p2):
                        springs_to_remove.add(s)
            # Remove all springs deleted in this run
            for s in springs_to_remove:
                springs.remove(s)
            temp_points[0] = Point(pos[0], pos[1])

    # Logic
    if UPDATE:
        for s in springs:
            s.update()
        for p in points:
            p.update(points)


    # Update
    redrawWindow(win)
    clock.tick(FPS)
