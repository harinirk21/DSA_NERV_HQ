# Maze with Keys and Doors — Shortest Path Solver

A Python-based maze solver that finds the shortest path from a starting point to an exit while collecting keys and unlocking doors. The project uses Breadth-First Search (BFS), supports CSV input/output, generates random solvable mazes, and provides animated visualization using Pygame.

## Features

- Finds the shortest path from `S` to `E`.
- Supports six key types: `a`–`f`.
- Allows entry through doors only when the matching key has been collected.
- Reads mazes from CSV files.
- Generates random mazes with guaranteed solvable routes.
- Exports the shortest path to a CSV file.
- Animates BFS exploration and the final path.
- Displays key inventory and door-unlocking events.
- Returns `-1` if the exit is unreachable.

## Technologies Used

- Python
- Breadth-First Search (BFS)
- Pygame
- CSV file handling

## Project Structure

```text
maze-project/
├── maze_keys_doors_visual.py
├── maze_input.csv
├── maze_solution.csv
└── README.md
```

## Maze Symbols

| Symbol | Description |
|---|---|
| `S` | Starting position |
| `E` | Exit |
| `.` | Open cell |
| `#` | Wall |
| `a`–`f` | Keys |
| `A`–`D`, `F` | Matching doors |
| `G` | Door requiring key `e` |
| `x` | Shortest-path marker for ordinary cells |

**Note:** The problem statement uses `E` for both the exit and a door. This implementation reserves `E` for the exit and uses `G` for the door requiring key `e`.

## Installation

Install Python 3.10 or newer, then install Pygame:

```bash
python -m pip install pygame
```

Pygame is only required for visualization. The solver and CSV processing can run without it.

## Usage

### 1. Solve a maze from a CSV file

```bash
python maze_keys_doors_visual.py --csv maze_input.csv --output maze_solution.csv
```

### 2. Display the maze in the terminal

```bash
python maze_keys_doors_visual.py --csv maze_input.csv --show-grid
```

### 3. Launch animated visualization

```bash
python maze_keys_doors_visual.py --csv maze_input.csv --output maze_solution.csv --visualize
```

### 4. Generate a random maze

```bash
python maze_keys_doors_visual.py --random --n 15 --t 3 --seed 42 --visualize
```

Arguments:

- `--n`: Grid dimension.
- `--t`: Number of key/door pairs, from 1 to 6.
- `--seed`: Random seed for reproducible mazes.
- `--wall-prob`: Probability of generating walls outside the protected route.
- `--output`: Output CSV filename.
- `--show-grid`: Display the maze and path in the terminal.
- `--visualize`: Launch the Pygame animation.
- `--delay`: Animation delay in milliseconds.

## Input Format

The input CSV must contain a square grid, with one cell per field.

Example:

```csv
S,.,#,#,#
.,a,A,.,E
.,.,.,.,.
#,#,#,#,#
.,.,.,.,.
```

The program validates the grid dimensions, symbols, and start and exit positions.

## Algorithm

The project uses **Breadth-First Search (BFS)** because every movement has the same cost.

Each search state contains:

`(row, column, key_mask)`

The key mask records which keys the player has collected. This allows the algorithm to distinguish between reaching the same cell with different inventories.

The algorithm:

1. Adds the starting state to a queue.
2. Explores neighbouring cells in four directions.
3. Rejects walls and doors whose keys have not been collected.
4. Updates the key mask when entering a key cell.
5. Records parent states for path reconstruction.
6. Stops when the exit is reached.
7. Reconstructs the shortest path and exports it to CSV.

## Complexity Analysis

Let `N` be the grid dimension and `K` be the number of key types.

- **Time complexity:** `O(N² × 2^K)`
- **Space complexity:** `O(N² × 2^K)`

There are at most `N² × 2^K` distinct position and key-mask states.

## Output

The program prints the shortest distance in moves.

- A non-negative integer indicates the shortest distance.
- `-1` indicates that no valid route exists.

When a route exists, the program generates a CSV file marking ordinary cells on the path with `x`. The original start, exit, key and door symbols are preserved.

## Visualization Controls

- **Space:** Pause or resume.
- **R:** Restart the animation.
- **Esc:** Close the visualization.

The GUI uses colours to distinguish walls, open cells, the start, the exit, and key/door pairs. It displays the key inventory and highlights the final shortest path.

## Limitations

- Animated visualization requires Pygame and a graphical desktop.
- `G` represents the door for key `e` because `E` is reserved for the exit.
- Arbitrary CSV mazes may not have a valid path.
- The visualization is a desktop application, not a web application.

## License

Add an appropriate license before distributing the project publicly.
