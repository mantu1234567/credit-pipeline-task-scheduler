from z3 import Solver, Int, And, Or, Sum, If, sat
from generator import generate_instance

benchmarks = [
    {"n": 8, "K": 3, "density": 0.3, "seed": 1, "type": "Small"},
    {"n": 10, "K": 4, "density": 0.4, "seed": 2, "type": "Small"},
    {"n": 12, "K": 4, "density": 0.5, "seed": 3, "type": "Small"},
    {"n": 50, "K": 8, "density": 0.25, "seed": 10, "type": "Medium"},
    {"n": 100, "K": 10, "density": 0.30, "seed": 11, "type": "Medium"},
    {"n": 150, "K": 12, "density": 0.35, "seed": 12, "type": "Medium"},
    {"n": 200, "K": 15, "density": 0.40, "seed": 20, "type": "Stress"},
    {"n": 200, "K": 5, "density": 0.60, "seed": 21, "type": "Tight K (Stress)"},
    {"n": 200, "K": 20, "density": 0.10, "seed": 22, "type": "Sparse Conflict (Stress)"}
]

for b in benchmarks:
    instance = generate_instance(b["n"], b["K"], conflict_density=b["density"], seed=b["seed"])
    
    n = b["n"]
    K = b["K"]
    conflicts = instance["conflicts"]
    resources = instance["resources"]
    capacities = instance["capacities"]
    windows = instance["windows"]
    
    s = Solver()
    
    # Task assignment variables: task_vars[i] is the slot index for task i
    task_vars = [Int(f"t_{i}") for i in range(n)]
    
    # SLA constraints (F3)
    for i in range(n):
        lo, hi = windows[i]
        s.add(And(task_vars[i] >= lo, task_vars[i] <= hi))
        
    # Conflict constraints (F1)
    for u, v in conflicts:
        s.add(task_vars[u] != task_vars[v])
        
    # Capacity constraints (F2)
    # For each slot slot_idx, and each resource dimension r:
    # sum of resources[i][r] for all tasks assigned to slot_idx <= capacities[slot_idx][r]
    for slot_idx in range(K):
        for r in range(4):
            # Sum of resource requirements if task is in slot_idx
            res_sum = Sum([If(task_vars[i] == slot_idx, resources[i][r], 0.0) for i in range(n)])
            s.add(res_sum <= capacities[slot_idx][r])
            
    res = s.check()
    print(f"Instance n={b['n']}, K={b['K']}, density={b['density']}, seed={b['seed']} ({b['type']}):")
    if res == sat:
        print("  --> TRUE FEASIBLE (Z3 found a valid assignment)")
    else:
        print("  --> TRUE INFEASIBLE (Z3 proved no assignment exists)")
