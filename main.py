import pygame
import osmnx as ox
import networkx as nx
import heapq
import math
import time

# ========== CONFIG ==========
WIDTH, HEIGHT = 1000, 800
FPS = 60
STEPS_PER_FRAME = 5   # smooth pacing
CITY = "Manhattan, New York, USA"
# ============================

# Colors
BLACK = (10, 10, 30)
GREY = (50, 50, 80)          # Base map roads
NEON_BLUE = (0, 180, 255)    # Start & Goal
NEON_GRAY = (180, 180, 200)  # Exploration lines
CYAN = (0, 255, 255)         # Final path

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Cyberpunk Pathfinder")

# ========== LOAD MAP ==========
print(f"Downloading map for {CITY}...")
G = ox.graph_from_place(CITY, network_type="drive")
G = nx.convert_node_labels_to_integers(G)
pos = {n: (d["x"], d["y"]) for n, d in G.nodes(data=True)}
print(f"✅ Map loaded: {len(G.nodes)} nodes, {len(G.edges)} edges")

# Normalize positions
xs, ys = zip(*pos.values())
min_x, max_x = min(xs), max(xs)
min_y, max_y = min(ys), max(ys)

def to_screen(x, y):
    sx = int((x - min_x) / (max_x - min_x) * (WIDTH - 40) + 20)
    sy = int((y - min_y) / (max_y - min_y) * (HEIGHT - 40) + 20)
    return sx, HEIGHT - sy

# ========== BACKGROUND ==========
def draw_background():
    bg = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        c = int(20 + (y / HEIGHT) * 40)  # purple gradient
        pygame.draw.line(bg, (c//2, 0, c), (0, y), (WIDTH, y))
    screen.blit(bg, (0, 0))

# ========== ROADS ==========
def draw_roads():
    for u, v in G.edges():
        x1, y1 = to_screen(*pos[u])
        x2, y2 = to_screen(*pos[v])
        pygame.draw.line(screen, (80, 40, 20), (x1, y1), (x2, y2), 1)  # faint orange neon

# ========== A* ==========
def heuristic(a, b):
    (x1, y1), (x2, y2) = pos[a], pos[b]
    return math.hypot(x1 - x2, y1 - y2)

def astar_steps(start, goal):
    frontier = [(0, start)]
    came_from = {start: None}
    cost_so_far = {start: 0}

    while frontier:
        _, current = heapq.heappop(frontier)

        if current == goal:
            path = []
            while current is not None:
                path.append(current)
                current = came_from[current]
            path.reverse()
            yield {"final_path": path, "came_from": came_from}
            return

        for neigh in G.neighbors(current):
            edge_data = list(G[current][neigh].values())[0]
            new_cost = cost_so_far[current] + edge_data.get("length", 1)
            if neigh not in cost_so_far or new_cost < cost_so_far[neigh]:
                cost_so_far[neigh] = new_cost
                priority = new_cost + heuristic(neigh, goal)
                heapq.heappush(frontier, (priority, neigh))
                came_from[neigh] = current

        yield {"frontier": [n for _, n in frontier], "came_from": came_from}

# ========== VISUAL HELPERS ==========
def draw_glow_line(x1, y1, x2, y2, base_color, life):
    intensity = life / 30
    bright = tuple(min(255, int(c * intensity)) for c in base_color)
    # outer aura
    pygame.draw.line(screen, bright, (x1, y1), (x2, y2), 6)
    # core
    pygame.draw.line(screen, base_color, (x1, y1), (x2, y2), 2)

def draw_final_path(path, elapsed):
    pulse = 1 + 0.3 * math.sin(elapsed * 4)
    for i in range(len(path) - 1):
        x1, y1 = to_screen(*pos[path[i]])
        x2, y2 = to_screen(*pos[path[i+1]])
        # aura
        pygame.draw.line(screen, (255, 200, 100), (x1, y1), (x2, y2), int(6 * pulse))
        # core
        pygame.draw.line(screen, CYAN, (x1, y1), (x2, y2), int(3 * pulse))

def draw_glow_node(node, elapsed):
    if node is None:
        return
    x, y = to_screen(*pos[node])
    pulse = (math.sin(elapsed * 3) + 1) / 2
    for r, alpha in [(20, 40), (14, 100), (10, 180)]:
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(s, (*NEON_BLUE, alpha), (x, y), int(r * (1 + 0.3 * pulse)))
        screen.blit(s, (0, 0))
    pygame.draw.circle(screen, NEON_BLUE, (x, y), 6 + int(2 * pulse))

# ========== MAIN LOOP ==========
steps = None
path = None
found = False
start_node, goal_node = None, None
start_time = time.time()

fading_lines = []  # (x1, y1, x2, y2, life)

running = True
while running:
    draw_background()
    draw_roads()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            nearest = min(pos, key=lambda n: (to_screen(*pos[n])[0] - mx)**2 + (to_screen(*pos[n])[1] - my)**2)
            if start_node is None:
                start_node = nearest
                print(f"Start set: {start_node}")
            elif goal_node is None:
                goal_node = nearest
                print(f"Goal set: {goal_node}")
                steps = astar_steps(start_node, goal_node)
                found = False
                path = None
                fading_lines.clear()

    if steps and not found:
        try:
            for _ in range(STEPS_PER_FRAME):
                frame = next(steps)

                if "final_path" in frame:
                    path = frame["final_path"]
                    found = True
                    break

                for node in frame["frontier"]:
                    p = []
                    c = node
                    while c is not None:
                        p.append(c)
                        c = frame["came_from"].get(c)
                    p = p[::-1]
                    for i in range(len(p) - 1):
                        x1, y1 = to_screen(*pos[p[i]])
                        x2, y2 = to_screen(*pos[p[i+1]])
                        fading_lines.append([x1, y1, x2, y2, 30])

        except StopIteration:
            steps = None

    # draw fading exploration trails
    new_lines = []
    for x1, y1, x2, y2, life in fading_lines:
        if life > 0:
            draw_glow_line(x1, y1, x2, y2, NEON_GRAY, life)
            new_lines.append([x1, y1, x2, y2, life - 1])
    fading_lines = new_lines

    # draw final path
    if found and path:
        elapsed = time.time() - start_time
        draw_final_path(path, elapsed)

    # draw start/end glow
    elapsed = time.time() - start_time
    draw_glow_node(start_node, elapsed)
    draw_glow_node(goal_node, elapsed)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
