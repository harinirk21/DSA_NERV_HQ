import argparse
import csv
import random
from collections import deque
from pathlib import Path

KEYS = "abcdef"
# E is reserved for the exit, so G represents the door for key e.
DOOR_TO_KEY = {"A": "a", "B": "b", "C": "c", "D": "d", "F": "f", "G": "e"}
KEY_TO_DOOR = {v: k for k, v in DOOR_TO_KEY.items()}
ALLOWED = set(".#SEabcdefABCDFG")


def read_grid_csv(filename):
    with open(filename, "r", newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    rows = [row for row in rows if row and any(cell.strip() for cell in row)]
    if not rows:
        raise ValueError("CSV file is empty.")
    # Accept either one cell per CSV field, or one compact row per CSV record.
    if all(len(row) == 1 for row in rows) and all(len(row[0].strip()) > 1 for row in rows):
        grid = [list(row[0].strip()) for row in rows]
    else:
        grid = [[cell.strip() for cell in row] for row in rows]
    n = len(grid)
    if any(len(row) != n for row in grid):
        raise ValueError(f"Grid must be square (N x N); found row lengths {[len(r) for r in grid]}.")
    for r, row in enumerate(grid):
        for c, cell in enumerate(row):
            if len(cell) != 1 or cell not in ALLOWED:
                raise ValueError(f"Invalid cell {cell!r} at row {r+1}, column {c+1}.")
    validate_grid(grid)
    return grid


def validate_grid(grid):
    n = len(grid)
    if n == 0 or any(len(row) != n for row in grid):
        raise ValueError("Grid must be a non-empty square N x N grid.")
    starts = [(r, c) for r in range(n) for c in range(n) if grid[r][c] == "S"]
    exits = [(r, c) for r in range(n) for c in range(n) if grid[r][c] == "E"]
    if len(starts) != 1:
        raise ValueError(f"Grid must contain exactly one S; found {len(starts)}.")
    if len(exits) != 1:
        raise ValueError(f"Grid must contain exactly one E; found {len(exits)}.")
    return starts[0], exits[0]


def shortest_path(grid):
    """BFS. Returns distance, path states, and animation events."""
    start, exit_pos = validate_grid(grid)
    n = len(grid)
    key_bit = {key: 1 << i for i, key in enumerate(KEYS)}
    start_state = (start[0], start[1], 0)
    queue = deque([start_state])
    visited = {start_state}
    parent = {start_state: None}
    distance = {start_state: 0}
    events = [{"type": "visit", "pos": start, "mask": 0}]
    directions = ((-1, 0), (1, 0), (0, -1), (0, 1))

    while queue:
        state = queue.popleft()
        r, c, mask = state
        if (r, c) == exit_pos:
            path = []
            cur = state
            while cur is not None:
                path.append(cur)
                cur = parent[cur]
            path.reverse()
            events.append({"type": "solution", "path": path})
            return distance[state], path, events

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if not (0 <= nr < n and 0 <= nc < n):
                continue
            cell = grid[nr][nc]
            if cell == "#":
                continue
            if cell in DOOR_TO_KEY:
                needed = DOOR_TO_KEY[cell]
                if mask & key_bit[needed] == 0:
                    continue
            new_mask = mask
            if cell in key_bit:
                new_mask |= key_bit[cell]
            nxt = (nr, nc, new_mask)
            if nxt in visited:
                continue
            visited.add(nxt)
            parent[nxt] = state
            distance[nxt] = distance[state] + 1
            queue.append(nxt)
            events.append({"type": "visit", "pos": (nr, nc), "mask": new_mask})
            if cell in key_bit and not (mask & key_bit[cell]):
                events.append({"type": "key", "pos": (nr, nc), "key": cell, "mask": new_mask})
            if cell in DOOR_TO_KEY:
                events.append({"type": "door", "pos": (nr, nc), "door": cell, "mask": new_mask})
    return -1, [], events


def write_path_csv(grid, path, output_file):
    marked = [row[:] for row in grid]
    for r, c, _mask in path:
        if marked[r][c] == ".":
            marked[r][c] = "x"
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(marked)


def generate_solvable_maze(n, t, wall_probability=0.25, seed=None):
    if not 1 <= t <= 6:
        raise ValueError("T must be between 1 and 6.")
    if n < 2 * t + 3:
        raise ValueError(f"For T={t}, use N >= {2*t+3}.")
    if not 0 <= wall_probability < 1:
        raise ValueError("Wall probability must be in [0, 1).")
    rng = random.Random(seed)
    grid = [["." for _ in range(n)] for _ in range(n)]
    route = [(1, c) for c in range(n - 1)] + [(r, n - 2) for r in range(2, n - 1)]
    route = list(dict.fromkeys(route))
    grid[route[0][0]][route[0][1]] = "S"
    grid[route[-1][0]][route[-1][1]] = "E"
    available = route[1:-1]
    if len(available) < 2 * t:
        raise ValueError("Maze too small to place all key/door pairs on guaranteed route.")
    for i in range(t):
        available_key = available[2*i]
        available_door = available[2*i+1]
        grid[available_key[0]][available_key[1]] = KEYS[i]
        door = KEY_TO_DOOR[KEYS[i]]
        grid[available_door[0]][available_door[1]] = door
    protected = set(route)
    for r in range(n):
        for c in range(n):
            if (r, c) not in protected and rng.random() < wall_probability:
                grid[r][c] = "#"
    return grid


def print_grid(grid):
    for row in grid:
        print(" ".join(row))


def visualize(grid, events, distance, path, cell_size=48, delay=45):
    try:
        import pygame
    except ImportError:
        raise SystemExit("Visualization needs pygame. Install it with: python -m pip install pygame")

    pygame.init()
    n = len(grid)
    panel_h = 100
    cell_size = max(18, min(cell_size, 760 // n))
    width, height = n * cell_size, n * cell_size + panel_h
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Maze with Keys and Doors — BFS shortest path")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", max(14, cell_size // 2), bold=True)
    small = pygame.font.SysFont("consolas", 18)

    WHITE = (248, 248, 248); BLACK = (35, 38, 45); GREEN = (54, 180, 90)
    RED = (225, 75, 75); PATH = (80, 180, 245); VISITED = (205, 225, 245)
    GOLD = (255, 210, 70); PURPLE = (180, 130, 220); TEXT = (25, 30, 40)
    pair_colors = {
        "a": (255, 220, 90), "A": (255, 220, 90),
        "b": (100, 190, 255), "B": (100, 190, 255),
        "c": (120, 220, 150), "C": (120, 220, 150),
        "d": (220, 150, 240), "D": (220, 150, 240),
        "e": (255, 160, 110), "G": (255, 160, 110),
        "f": (130, 220, 220), "F": (130, 220, 220),
    }
    explored = set()
    final_path = set()
    unlocked = set()
    inventory = set()
    current = None
    event_index = 0
    paused = False
    finished = False
    last_step = pygame.time.get_ticks()

    def draw():
        screen.fill(WHITE)
        for r in range(n):
            for c in range(n):
                cell = grid[r][c]
                rect = pygame.Rect(c*cell_size, r*cell_size, cell_size, cell_size)
                color = WHITE
                if cell == "#": color = BLACK
                elif cell == "S": color = GREEN
                elif cell == "E": color = RED
                elif cell in pair_colors: color = pair_colors[cell]
                if (r, c) in explored and cell not in "#SE": color = VISITED
                if (r, c) in final_path and cell not in "#SE": color = PATH
                if cell in DOOR_TO_KEY and (r, c) in unlocked: color = WHITE
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, (160, 165, 175), rect, 1)
                if cell not in ".#x" or cell == "x":
                    label = cell
                    if cell in DOOR_TO_KEY and (r, c) in unlocked: label = "✓"
                    if cell == "x": label = "x"
                    rendered = font.render(label, True, WHITE if cell == "#" else TEXT)
                    screen.blit(rendered, rendered.get_rect(center=rect.center))
                if current == (r, c):
                    pygame.draw.circle(screen, (25, 85, 210), rect.center, max(5, cell_size//5), 3)
        y = n*cell_size
        pygame.draw.rect(screen, (238, 241, 246), (0, y, width, panel_h))
        status = "Shortest path found!" if finished and distance >= 0 else ("No path exists" if finished else "BFS searching…")
        if finished and distance >= 0:
            status += f"   Distance: {distance} moves"
        screen.blit(small.render(status, True, TEXT), (12, y+10))
        key_text = "Keys: " + (" ".join(sorted(inventory)) if inventory else "none")
        screen.blit(small.render(key_text, True, TEXT), (12, y+38))
        screen.blit(small.render("Space: pause/resume   R: restart   Esc: quit", True, TEXT), (12, y+66))
        pygame.display.flip()

    running = True
    while running:
        now = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    explored.clear(); final_path.clear(); unlocked.clear(); inventory.clear()
                    current = None; event_index = 0; finished = False; paused = False
                    last_step = now
        if not paused and not finished and event_index < len(events) and now - last_step >= delay:
            ev = events[event_index]
            event_index += 1
            last_step = now
            if ev["type"] == "visit":
                explored.add(ev["pos"]); current = ev["pos"]
                mask = ev["mask"]
                inventory = {k for i, k in enumerate(KEYS) if mask & (1 << i)}
            elif ev["type"] == "key":
                inventory.add(ev["key"]); current = ev["pos"]
            elif ev["type"] == "door":
                unlocked.add(ev["pos"]); current = ev["pos"]
            elif ev["type"] == "solution":
                final_path = {(r, c) for r, c, _ in ev["path"]}
                current = ev["path"][-1][:2]
                finished = True
        elif event_index >= len(events):
            finished = True
        draw()
        clock.tick(60)
    pygame.quit()


def main():
    parser = argparse.ArgumentParser(description="Maze shortest path with keys/doors, CSV and animated visualization.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--csv", dest="csv_file", help="Input N x N maze CSV")
    source.add_argument("--random", action="store_true", help="Generate a random solvable maze")
    parser.add_argument("--n", type=int, help="Grid size for random mode")
    parser.add_argument("--t", type=int, help="Number of key/door types (1..6)")
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    parser.add_argument("--wall-prob", type=float, default=0.25, help="Random wall probability")
    parser.add_argument("--output", default="maze_solution.csv", help="Path-marked output CSV")
    parser.add_argument("--visualize", action="store_true", help="Open animated Pygame visualization")
    parser.add_argument("--delay", type=int, default=45, help="Milliseconds between animation steps")
    parser.add_argument("--show-grid", action="store_true", help="Print maze and path in terminal")
    args = parser.parse_args()
    if args.delay < 0:
        parser.error("--delay must be >= 0")
    try:
        if args.csv_file:
            grid = read_grid_csv(args.csv_file)
        else:
            if args.n is None or args.t is None:
                parser.error("--random requires both --n and --t")
            grid = generate_solvable_maze(args.n, args.t, args.wall_prob, args.seed)
        distance, path, events = shortest_path(grid)
        print(distance)
        if distance >= 0:
            write_path_csv(grid, path, args.output)
            print(f"Path CSV saved to: {Path(args.output).resolve()}")
        else:
            print("No path exists; output CSV was not created.")
        if args.show_grid:
            print("\nMaze:"); print_grid(grid)
            if path:
                marked = [row[:] for row in grid]
                for r, c, _ in path:
                    if marked[r][c] == ".": marked[r][c] = "x"
                print("\nShortest path:"); print_grid(marked)
        if args.visualize:
            visualize(grid, events, distance, path, delay=args.delay)
    except (ValueError, OSError, csv.Error) as exc:
        raise SystemExit(f"Error: {exc}")

if __name__ == "__main__":
    main()
