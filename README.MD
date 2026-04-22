*This project has been created as part of the 42 curriculum by ael-bakk.*

# Drone Network Simulation

## Description

This project simulates a networked drone delivery system as outlined in the 42 curriculum. Multiple drones must travel from a start hub to an end hub through a network of zones (nodes), each with their own properties such as type, capacity, and color. Connections have their own capacity as well. The aim is to optimize drone throughput and minimize total turns, while respecting all zone and link constraints. The output provides a colored, turn-by-turn trace of drone movements.

## Instructions

### Requirements & Installation

- Python 3.8+
- flake8, mypy

**To install dependencies:**
```bash
make install
```

### How to Run

```
make run MAP=path/to/your_map.txt
```

If `MAP` is not provided, it defaults to `map.txt`.
- The simulation will parse your map file, simulate the drones' journeys, and print step-by-step colored output in the terminal.

**Debug mode:**
```bash
make debug MAP=path/to/your_map.txt
```

### Additional Tasks

- **Linting**:  
  `make lint` (basic)  
  `make lint-strict` (strict mode)

- **Clean build and cache files:**  
  `make clean`

## Features

- Fast map parser and robust error handling.
- Strict enforcement of both zone (`max_drones`) and connection (`max_link_capacity`) constraints.
- Step-by-step colored visualization of drone movement.
- Full scheduling for minimal-turn solutions.
- OOP design (`GraphModel`, `Zone`, `Connection`, `Drone`, `Simulation`).
- Print turn and move statistics at the end.

## Algorithm Choices and Implementation

- **Pathfinding:**  
  Uses BFS with priority-neighbor preference per 42's project requirements. Blocked zones are automatically avoided.
- **Scheduler:**  
  At each turn, all eligible drones plan their move simultaneously. Drones leaving a zone free a slot for entrants within the same turn.
- **State Handling:**  
  Restricted zones create "in-flight" state; drones land after one turn. 
- **Constraints:**  
  Both zone and connection usage are strictly checked every turn.
- **Output:**  
  Drone movements are printed as `D<ID>-<zone>` or `D<ID>-<from>-<to>` (for in-flight), using zone colors for visual clarity.

## Visual Representation

- Terminal output uses zone-specific ANSI colors, as defined per the map.
- Each turn’s moves are displayed in order by drone ID, making the simulation trace easy to follow.

## Resources

- [Breadth-First Search - Wikipedia](https://en.wikipedia.org/wiki/Breadth-first_search)
- [ANSI Escape Codes (Colors)](https://en.wikipedia.org/wiki/ANSI_escape_code#Colors)
- [Network Flow Concepts](https://en.wikipedia.org/wiki/Network_flow)
- [42 Subject PDF]

### AI Use

- AI tools (GitHub Copilot & ChatGPT) were used for:
    - Edge case handling
    - Visual output design
    - Documentation drafting
    - Reviewing code logic

## Technical Choices

- Only Python standard libraries are used for portability.
- BFS with priority-first neighbor sort as required by subject.
- Colors and terminal formatting are pure ANSI for compatibility.

