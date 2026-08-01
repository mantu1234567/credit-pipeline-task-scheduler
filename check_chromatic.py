import random
from generator import generate_instance

# We will check if the conflict graph can be colored with K colors using a simple greedy coloring with restarts
def greedy_coloring(n, conflicts):
    adj = [[] for _ in range(n)]
    for i, j in conflicts:
        adj[i].append(j)
        adj[j].append(i)
        
    # Greedy coloring with random ordering to find a upper bound on chromatic number
    best_colors = n
    for _ in range(100):
        order = list(range(n))
        random.shuffle(order)
        colors = [-1] * n
        for u in order:
            used = set()
            for v in adj[u]:
                if colors[v] != -1:
                    used.add(colors[v])
            # assign smallest available color
            c = 0
            while c in used:
                c += 1
            colors[u] = c
        num_colors = max(colors) + 1
        if num_colors < best_colors:
            best_colors = num_colors
    return best_colors

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
    chromatic_approx = greedy_coloring(b["n"], instance["conflicts"])
    print(f"Instance n={b['n']}, K={b['K']}, density={b['density']}, seed={b['seed']}:")
    print(f"  Approx Chromatic Number of Conflict Graph: {chromatic_approx}")
    print(f"  Slots (K) available: {b['K']}")
    if chromatic_approx > b['K']:
        print("  --> MATHEMATICALLY INFEASIBLE: Chromatic number > K (Graph cannot be colored with K colors)")
    else:
        print("  --> Mathematically feasible for coloring (might fail on resource/SLA constraints)")
