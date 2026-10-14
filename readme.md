# 🧠 DSA NERV HQ

### Data Structures & Algorithms | Problem Solving | Algorithm Visualization

A collection of Data Structures and Algorithms (DSA) implementations, problem-solving approaches, and algorithmic experiments designed to strengthen logical thinking, explore efficient solutions, and understand how algorithms work.

---

## 📌 Table of Contents

- [About the Project](#-about-the-project)
- [Objectives](#-objectives)
- [Algorithms and Problems](#-algorithms-and-problems)
- [Featured Project: Maze with Keys and Doors](#-featured-project-maze-with-keys-and-doors--shortest-path)
- [Algorithm and Approach](#-algorithm-and-approach)
- [Complexity Analysis](#-complexity-analysis)
- [Project Structure](#-project-structure)
- [Installation and Setup](#-installation-and-setup)
- [Usage](#-usage)
- [Input and Output](#-input-and-output)
- [Testing and Edge Cases](#-testing-and-edge-cases)
- [Future Improvements](#-future-improvements)
- [Contributing](#-contributing)
- [License](#-license)

---

## 📖 About the Project

**DSA NERV HQ** is a repository dedicated to implementing and exploring Data Structures and Algorithms through practical programming problems.

The repository focuses on translating problem statements into efficient algorithms, understanding their computational complexity, and developing solutions that are easy to execute, test, and maintain.

The featured maze-solving module demonstrates how graph traversal, bitmasking, and path reconstruction can be combined to solve a shortest-path problem involving keys and locked doors.

## 🎯 Objectives

- Strengthen problem-solving and algorithmic thinking.
- Implement efficient algorithms for practical problems.
- Understand time and space complexity.
- Explore graph traversal and state-space search.
- Demonstrate algorithm behavior through visualization.
- Develop readable, reusable, and testable code.
- Document the reasoning behind each implementation.

---

## 🗂️ Algorithms and Problems

The repository can be navigated by problem or algorithm category.

| Category | Concepts |
|---|---|
| Graph Algorithms | Graph traversal and pathfinding |
| Search Algorithms | Breadth-First Search (BFS) |
| Bit Manipulation | Bitmasks and state tracking |
| Pathfinding | Shortest-path computation and path reconstruction |
| Visualization | Animated algorithm execution using Pygame |

*The table highlights the concepts covered by the featured maze solver. Add other categories as corresponding implementations become available.*

---

## 🧩 Featured Project: Maze with Keys and Doors — Shortest Path

### Problem Statement

Given an \(N \times N\) grid, find the shortest valid path from the starting position `S` to the exit `E`.

The grid contains walls, open cells, keys, and matching doors. A door can only be entered after collecting its corresponding key.

If no valid path exists, the algorithm returns `-1`.

### Maze Symbols

| Symbol | Description |
|---|---|
| `S` | Starting position |
| `E` | Exit |
| `.` | Open cell |
| `#` | Wall |
| `a`–`f` | Keys |
| `A`–`F` | Matching doors |

**Special symbol convention:** The implementation reserves `E` for the exit. To avoid ambiguity, `G` represents the door that requires key `e`. The remaining key and door symbols follow the conventions implemented by the solver.

### Key Features

- **Shortest-path search:** Uses BFS to find a shortest valid route.
- **Key collection:** Tracks collected keys using bitmasking.
- **Door unlocking:** Prevents entry through a locked door until its matching key is collected.
- **State-aware exploration:** Tracks both the current position and the collected keys.
- **Path reconstruction:** Uses parent pointers to reconstruct the solution.
- **CSV input and output:** Supports reading a maze from a CSV file and writing the path-marked solution.
- **Random maze generation:** Supports generating a maze using command-line parameters.
- **Interactive visualization:** Uses Pygame to animate the search, show key collection and door unlocking, and highlight the final path.

---

## 🧠 Algorithm and Approach

The solver uses **Breadth-First Search (BFS)** with an expanded state representation.

### 1. State Representation

Each state is represented as:

`(row, column, key_mask)`

Where:
- `row` and `column` identify the current grid position.
- `key_mask` represents the set of keys collected so far.

### 2. Bitmasking

Each key type is represented by one bit in an integer. For example, if keys `a` and `c` have been collected, their corresponding bits are set in the mask.

This allows the solver to track up to six key types efficiently.

### 3. BFS Traversal

BFS explores valid states level by level using a queue. Since each valid grid move has the same cost, the first discovered exit state gives a shortest path in terms of the number of moves.

### 4. Door Validation

Before entering a door, the solver checks whether the corresponding key is present in the current key mask. If the key has not been collected, the move is rejected.

### 5. Visited-State Tracking

The solver tracks visited combinations of position and key inventory rather than tracking only the grid position.

This is essential because reaching the same cell with different keys can lead to different future possibilities.

### 6. Path Reconstruction

Parent pointers record the predecessor of each discovered state. Once the exit is reached, these pointers are followed backward to reconstruct the shortest path.

### 7. CSV Output

The solution is written to a CSV file, with the shortest path marked using `x`. The implementation preserves important maze symbols, including the start, exit, keys, and doors.

### 8. Visualization

Pygame provides an animated representation of the search process, including exploration, key collection, door unlocking, and the final shortest path.

---

## 📊 Complexity Analysis

Let:

- \(N\) be the dimension of the square grid.
- \(K\) be the number of key types, where \(K \leq 6\).

There are at most \(N^2\) grid positions and \(2^K\) possible key masks.

Therefore, the maximum number of distinct search states is:

\[
N^2 \times 2^K
\]

Assuming a constant number of possible moves per state:

| Metric | Complexity |
|---|---|
| Time Complexity | \(O(N^2 \times 2^K)\) |
| Space Complexity | \(O(N^2 \times 2^K)\) |

The time complexity accounts for exploring the state space. The space complexity accounts for visited states, the BFS queue, and parent pointers.

---

## 📁 Project Structure

The following is an illustrative structure. Update it to match the actual files in the repository.

```text
DSA_NERV_HQ/
├── README.md
├── maze_keys_doors_visual.py
├── complex_maze.csv
├── complex_solution.csv
├── requirements.txt
└── assets/
    └── maze_visualization.gif
```

| File or Directory | Purpose |
|---|---|
| `README.md` | Project documentation |
| `maze_keys_doors_visual.py` | Maze-solving algorithm and visualization |
| `complex_maze.csv` | Example maze input |
| `complex_solution.csv` | Generated solution output |
| `requirements.txt` | Python dependency list |
| `assets/` | Optional screenshots and demonstration GIFs |

Only include files and directories that actually exist.

---

## ⚙️ Installation and Setup

### Prerequisites

- Python 3
- pip, the Python package installer
- Pygame for graphical visualization

### Step 1: Clone the Repository

```bash
git clone https://github.com/harinirk21/DSA_NERV_HQ.git
```

### Step 2: Navigate to the Project

```bash
cd DSA_NERV_HQ
```

### Step 3: Install Dependencies

Install Pygame:

```bash
python -m pip install pygame
```

If a `requirements.txt` file is available and lists all required dependencies, use:

```bash
python -m pip install -r requirements.txt
```

---

## 🚀 Usage

Run the commands from the directory containing `maze_keys_doors_visual.py`.

### 1. Solve a Maze from a CSV File

```bash
python maze_keys_doors_visual.py \
  --csv complex_maze.csv \
  --output complex_solution.csv \
  --visualize
```

This command reads the maze from `complex_maze.csv`, computes a shortest valid path, writes the result to `complex_solution.csv`, and launches the visualization.

### 2. Generate and Solve a Random Maze

```bash
python maze_keys_doors_visual.py \
  --random \
  --n 15 \
  --t 6 \
  --seed 42 \
  --visualize
```

| Parameter | Description |
|---|---|
| `--random` | Enables random maze generation |
| `--n 15` | Sets the maze dimension to 15 × 15 |
| `--t 6` | Supplies the generator parameter `t` |
| `--seed 42` | Supplies a seed for reproducible generation |
| `--visualize` | Enables graphical visualization |

The precise meaning of `--t` depends on the implementation. Check the script's argument parser before documenting it more specifically.

### 3. Run Without Visualization

Omit the `--visualize` option to run the solver without requesting the Pygame animation:

```bash
python maze_keys_doors_visual.py \
  --csv complex_maze.csv \
  --output complex_solution.csv
```

This mode is supported only if the script permits execution without visualization.

---

## 📥 Input and Output

### Input

The solver accepts a maze stored in CSV format.

Example conceptual grid:

```text
S,.,a,#,.
#,.,.,A,.
.,.,#,.,E
```

This example illustrates the maze symbols and is not guaranteed to be a valid test case for the implementation's CSV parser.

### Output

The solver is designed to provide:

1. The shortest path length, or `-1` if no valid route exists.
2. A CSV file containing the maze with the shortest path marked using `x`.
3. An animated visualization when `--visualize` is specified.

The start, exit, keys, and doors are preserved in the path-marked output.

For reproducible documentation, add a verified example containing an actual input CSV, its exact terminal output, and the generated solution CSV.

---

## 🧪 Testing and Edge Cases

The maze solver should be tested against scenarios that exercise both ordinary pathfinding and key-dependent movement.

| Test Case | Expected Behavior |
|---|---|
| Direct path from `S` to `E` | Finds the shortest route |
| Exit blocked by walls | Returns `-1` if no valid route exists |
| Door encountered before its key | Rejects entry through the locked door |
| Key collected before reaching a door | Allows entry through the matching door |
| Same cell reached with different key masks | Treats distinct states independently |
| Multiple keys and doors | Tracks key inventory correctly |
| Key not required for the shortest route | Does not collect unnecessary keys unless the route requires them |
| Random maze with a fixed seed | Produces reproducible input if generation is deterministic |

These are recommended test scenarios, not claims that automated tests currently exist.

---

## 🔮 Future Improvements

Potential extensions for the repository include:

- Add automated unit tests for individual algorithms and edge cases.
- Include sample input and output files for each problem.
- Add screenshots or GIFs demonstrating algorithm execution.
- Introduce a consistent documentation template for every DSA problem.
- Add difficulty labels and topic tags to the problem index.
- Compare BFS with algorithms such as Dijkstra's algorithm and A* where appropriate.
- Improve error handling for malformed CSV files and invalid maze symbols.
- Add continuous integration to run automated tests on every proposed change.
- Document the time and space complexity of every implementation.
- Add contribution guidelines for developers who want to extend the project.

---

## 🤝 Contributing

Contributions and suggestions are welcome.

To contribute:

1. Fork the repository.
2. Create a branch for your changes.
3. Implement your solution or improvement.
4. Test the changes against relevant cases.
5. Update the documentation where necessary.
6. Submit a pull request describing the changes.

Please keep implementations readable, document important algorithmic decisions, and include test cases for new functionality where practical.

---

## 📄 License

No license is specified in this README. If you intend to make the project open source, choose an appropriate license and add the corresponding `LICENSE` file before describing the repository as available under that license.

---

## ⭐ Acknowledgements

Built as a learning and development project focused on algorithmic problem-solving, efficient implementations, and practical demonstrations of Data Structures and Algorithms.

If you find the project useful, consider starring the repository and sharing suggestions for future improvements.

**Repository:** [harinirk21/DSA_NERV_HQ](https://github.com/harinirk21/DSA_NERV_HQ)
