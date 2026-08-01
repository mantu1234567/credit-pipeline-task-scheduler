import time
import json
import sys
from generator import generate_instance
from solver import solve_heuristic, solve_brute_force

# Define the 9 benchmark instances
benchmarks = [
    # Small instances
    {"n": 8, "K": 3, "density": 0.3, "seed": 1, "type": "Small"},
    {"n": 10, "K": 4, "density": 0.4, "seed": 2, "type": "Small"},
    {"n": 12, "K": 4, "density": 0.5, "seed": 3, "type": "Small"},
    
    # Medium instances
    {"n": 50, "K": 8, "density": 0.25, "seed": 10, "type": "Medium"},
    {"n": 100, "K": 10, "density": 0.30, "seed": 11, "type": "Medium"},
    {"n": 150, "K": 12, "density": 0.35, "seed": 12, "type": "Medium"},
    
    # Stress instances
    {"n": 200, "K": 15, "density": 0.40, "seed": 20, "type": "Stress"},
    {"n": 200, "K": 5, "density": 0.60, "seed": 21, "type": "Tight K (Stress)"},
    {"n": 200, "K": 20, "density": 0.10, "seed": 22, "type": "Sparse Conflict (Stress)"}
]

def run_benchmarks():
    results = []
    
    print("Running benchmarks...")
    print(f"{'Instance (n, K, density)':<30} | {'Type':<12} | {'Feasible':<8} | {'Heur Pen':<10} | {'Brute Pen':<10} | {'Ratio':<6} | {'Runtime (ms)':<12}")
    print("-" * 105)
    
    for b in benchmarks:
        instance = generate_instance(b["n"], b["K"], conflict_density=b["density"], seed=b["seed"])
        
        # Run heuristic solver
        heur_res = solve_heuristic(instance)
        
        # Run brute-force solver for small instances only
        opt_penalty = None
        if b["type"] == "Small":
            brute_res = solve_brute_force(instance)
            if brute_res["feasible"]:
                opt_penalty = brute_res["penalty"]
                
        # Calculate approximation ratio
        ratio = "N/A"
        if opt_penalty is not None and heur_res["feasible"]:
            ratio = f"{heur_res['penalty'] / opt_penalty:.3f}"
            
        brute_pen_str = f"{opt_penalty:.2f}" if opt_penalty is not None else "N/A"
        heur_pen_str = f"{heur_res['penalty']:.2f}" if heur_res["feasible"] else "Infeasible"
        feas_str = "Yes" if heur_res["feasible"] else "No"
        
        inst_name = f"n={b['n']}, K={b['K']}, d={b['density']}"
        print(f"{inst_name:<30} | {b['type']:<12} | {feas_str:<8} | {heur_pen_str:<10} | {brute_pen_str:<10} | {ratio:<6} | {heur_res['runtime_ms']:<12}")
        
        results.append({
            "n": b["n"],
            "K": b["K"],
            "density": b["density"],
            "type": b["type"],
            "feasible": heur_res["feasible"],
            "penalty": heur_res["penalty"] if heur_res["feasible"] else None,
            "runtime_ms": heur_res["runtime_ms"],
            "opt_penalty": opt_penalty,
            "ratio": float(ratio) if ratio != "N/A" else None
        })
        
    # Attempt to plot charts
    try:
        import matplotlib.pyplot as plt
        
        # Filter feasible instances for plotting
        plot_data = [r for r in results if r["feasible"] and r["type"] in ["Small", "Medium", "Stress"]]
        plot_data.sort(key=lambda x: x["n"])
        
        ns = [r["n"] for r in plot_data]
        penalties = [r["penalty"] for r in plot_data]
        runtimes = [r["runtime_ms"] for r in plot_data]
        
        # Plot 1: Penalty vs n
        plt.figure(figsize=(8, 5))
        plt.plot(ns, penalties, marker='o', color='#1f77b4', linewidth=2)
        plt.title('PW-RAD Algorithm: Penalty vs Number of Tasks (n)')
        plt.xlabel('Number of Tasks (n)')
        plt.ylabel('Total Penalty')
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.savefig('/home/hp/Documents/scoreme_assignment/penalty_vs_n.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Plot 2: Runtime vs n
        plt.figure(figsize=(8, 5))
        plt.plot(ns, runtimes, marker='s', color='#2ca02c', linewidth=2)
        plt.title('PW-RAD Algorithm: Execution Runtime vs Number of Tasks (n)')
        plt.xlabel('Number of Tasks (n)')
        plt.ylabel('Runtime (ms)')
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.savefig('/home/hp/Documents/scoreme_assignment/runtime_vs_n.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("\n[SUCCESS] Saved benchmark charts to Documents/scoreme_assignment/")
    except ImportError:
        print("\n[WARNING] matplotlib is not installed. Skipping chart generation.")
        
if __name__ == "__main__":
    run_benchmarks()
