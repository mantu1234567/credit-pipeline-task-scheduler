import json
import argparse
import sys
from generator import generate_instance
from solver import solve_heuristic, solve_brute_force, check_feasibility

def main():
    parser = argparse.ArgumentParser(description="ScoreMe MSME Task Scheduler CLI")
    
    # Mode 1: File-based input
    parser.add_argument("--file", type=str, help="Path to input JSON file containing the instance")
    
    # Mode 2: CLI-based generation parameters
    parser.add_argument("--n", type=int, help="Number of tasks")
    parser.add_argument("--K", type=int, help="Number of slots")
    parser.add_argument("--density", type=float, help="Conflict density (0.0 to 1.0)")
    parser.add_argument("--seed", type=int, help="Random seed for generation")
    
    # Option to run brute-force instead of heuristic
    parser.add_argument("--brute", action="store_true", help="Run brute-force solver instead of PW-RAD")
    
    args = parser.parse_args()
    
    instance = None
    
    if args.file:
        try:
            with open(args.file, 'r') as f:
                instance = json.load(f)
        except Exception as e:
            print(json.dumps({
                "assignment": {},
                "penalty": -1.0,
                "runtime_ms": 0,
                "feasible": False,
                "violation_reason": f"Failed to read input JSON file: {str(e)}"
            }, indent=2))
            sys.exit(1)
    elif args.n is not None and args.K is not None:
        density = args.density if args.density is not None else 0.3
        seed = args.seed if args.seed is not None else 42
        try:
            instance = generate_instance(args.n, args.K, conflict_density=density, seed=seed)
        except Exception as e:
            print(json.dumps({
                "assignment": {},
                "penalty": -1.0,
                "runtime_ms": 0,
                "feasible": False,
                "violation_reason": f"Failed to generate instance: {str(e)}"
            }, indent=2))
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)
        
    # Solve
    if args.brute:
        result = solve_brute_force(instance)
    else:
        result = solve_heuristic(instance)
        
    # Double-check feasibility if solver claims it is feasible
    if result['feasible']:
        ok, reason = check_feasibility(result['assignment'], instance)
        if not ok:
            result['feasible'] = False
            result['violation_reason'] = f"Feasibility validation failed: {reason}"
            result['assignment'] = {}
            result['penalty'] = -1.0
            
    # Print the JSON output to stdout as required by the spec
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
