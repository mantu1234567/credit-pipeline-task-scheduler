# Credit Pipeline Task Scheduler

This repository contains a high-performance scheduling system designed to assign credit pipeline tasks to discrete processing slots while satisfying complex conflict, capacity, and SLA constraints.

## Project Structure

* **`solver.py`**: Contains the core scheduler implementation:
  * **PW-RAD (Priority-Weighted Resource-Aware DSATUR)**: A custom polynomial-time heuristic designed for highly constrained scheduling.
  * **Brute-Force Solver**: A branch-and-bound solver to calculate the exact mathematically optimal solution for small instances.
* **`generator.py`**: The credit pipeline instance generator (generates test cases with random SLA windows, resource demands, conflicts, and priority weights).
* **`run.py`**: The CLI entrypoint. Supports loading instance files or generating tasks dynamically.
* **`test_solver.py`**: Unit tests covering edge cases (all-conflict graphs, zero-capacity slots, tight SLA windows, and single-task instances).
* **`benchmark.py`**: Runs the algorithm against the 9 standard benchmark scenarios, prints performance results, and generates visualization charts.
* **`report.md`**: The comprehensive technical report covering NP-hardness proofs, penalty function design, pseudocode, approximation bounds, and the design journal.
* **`report.tex`**: LaTeX source code of the technical report for PDF compilation.

---

## Getting Started

### Prerequisites
* Python 3.10+
* Virtual Environment module (`python3-venv`)

### Installation & Setup

1. **Clone or copy the directory** to your local machine.
2. **Navigate into the folder**:
   ```bash
   cd scoreme_assignment
   ```
3. **Set up the virtual environment** and install dependencies (required only for plotting benchmark charts):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install matplotlib
   ```

---

## Usage Instructions

### 1. Running Unit Tests
To verify the solver handles edge cases correctly, run:
```bash
python3 test_solver.py
```

### 2. Running Benchmarks & Generating Charts
To execute the scheduler across the 9 test scenarios (Small, Medium, and Stress instances) and generate performance charts:
```bash
# Make sure the virtual environment is activated, or call its python parser directly:
./venv/bin/python benchmark.py
```
This prints the execution table to stdout and generates:
* `penalty_vs_n.png` (Penalty growth curve)
* `runtime_vs_n.png` (Runtime scaling curve)

### 3. Running Single Instances
You can run the scheduler dynamically from the command line:

* **Heuristic Mode (PW-RAD):**
  ```bash
  python3 run.py --n 10 --K 4 --density 0.4 --seed 2
  ```

* **Brute-Force Mode (Exact Optimal):**
  ```bash
  python3 run.py --n 10 --K 4 --density 0.4 --seed 2 --brute
  ```

* **File Mode (JSON Input):**
  ```bash
  python3 run.py --file input_instance.json
  ```
