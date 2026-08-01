import time
import math

def compute_penalty(assignment, instance, alpha=5.0, beta=2.0):
    """
    Computes the total penalty P(sigma) for a given task assignment.
    P(sigma) = P_base(sigma) + alpha * P_sla(sigma) + beta * P_balance(sigma)
    """
    tasks = instance['tasks']
    weights = instance['weights']
    windows = instance['windows']
    capacities = instance['capacities']
    resources = instance['resources']
    K = instance['K']
    
    task_to_idx = {t: i for i, t in enumerate(tasks)}
    
    # 1. Base Penalty (weighted slot index = delay)
    p_base = 0.0
    for task_id, slot in assignment.items():
        idx = task_to_idx[task_id]
        p_base += weights[idx] * slot
        
    # 2. SLA Proximity Risk Penalty
    p_sla = 0.0
    for task_id, slot in assignment.items():
        idx = task_to_idx[task_id]
        lo, hi = windows[idx]
        if hi > lo:
            proximity = (slot - lo) / (hi - lo)
            p_sla += weights[idx] * (proximity ** 2)
            
    # 3. Load Imbalance Penalty (Variance of resource usage percentages)
    slots_util = [[0.0] * 4 for _ in range(K)]
    for task_id, slot in assignment.items():
        idx = task_to_idx[task_id]
        for r in range(4):
            slots_util[slot][r] += resources[idx][r]
            
    p_balance = 0.0
    for r in range(4):
        utils = []
        for s in range(K):
            cap = capacities[s][r]
            if cap > 0:
                utils.append(slots_util[s][r] / cap)
            else:
                utils.append(0.0)
        mean_util = sum(utils) / K
        variance = sum((u - mean_util) ** 2 for u in utils) / K
        p_balance += variance
        
    return float(p_base + alpha * p_sla + beta * p_balance)

def check_feasibility(assignment, instance):
    """
    Validates whether the given assignment satisfies all feasibility constraints.
    """
    tasks = instance['tasks']
    conflicts = instance['conflicts']
    resources = instance['resources']
    capacities = instance['capacities']
    windows = instance['windows']
    K = instance['K']
    
    task_to_idx = {t: i for i, t in enumerate(tasks)}
    
    if len(assignment) != len(tasks):
        missing = set(tasks) - set(assignment.keys())
        return False, f"Incomplete assignment: missing {len(missing)} tasks."
        
    # Check SLA Windows (F3)
    for task_id, slot in assignment.items():
        idx = task_to_idx[task_id]
        lo, hi = windows[idx]
        if not (lo <= slot <= hi):
            return False, f"SLA Violation: Task {task_id} assigned to slot {slot}, SLA window is [{lo}, {hi}]."
            
    # Check Conflicts (F1)
    for i, j in conflicts:
        t_i = tasks[i]
        t_j = tasks[j]
        if t_i in assignment and t_j in assignment:
            if assignment[t_i] == assignment[t_j]:
                return False, f"Conflict Violation: Task {t_i} and {t_j} share slot {assignment[t_i]}."
                
    # Check Capacities (F2)
    slots_util = [[0.0] * 4 for _ in range(K)]
    for task_id, slot in assignment.items():
        idx = task_to_idx[task_id]
        for r in range(4):
            slots_util[slot][r] += resources[idx][r]
            
    for s in range(K):
        for r in range(4):
            if slots_util[s][r] > capacities[s][r] + 1e-9:
                return False, f"Capacity Violation: Slot {s} dimension {r} has usage {slots_util[s][r]:.2f} exceeding capacity {capacities[s][r]}."
                
    return True, ""

def solve_brute_force(instance):
    """
    Finds the mathematically optimal assignment by exhaustively searching the feasible space.
    """
    t_start = time.perf_counter()
    tasks = instance['tasks']
    conflicts = instance['conflicts']
    resources = instance['resources']
    capacities = instance['capacities']
    windows = instance['windows']
    K = instance['K']
    n = len(tasks)
    
    adj = [[] for _ in range(n)]
    for i, j in conflicts:
        adj[i].append(j)
        adj[j].append(i)
        
    best_assignment = None
    best_penalty = float('inf')
    
    current_assignment = [-1] * n
    slots_util = [[0.0] * 4 for _ in range(K)]
    
    def backtrack(task_idx):
        nonlocal best_assignment, best_penalty
        
        if task_idx == n:
            assignment_dict = {tasks[i]: current_assignment[i] for i in range(n)}
            penalty = compute_penalty(assignment_dict, instance)
            if penalty < best_penalty:
                best_penalty = penalty
                best_assignment = assignment_dict.copy()
            return
            
        lo, hi = windows[task_idx]
        for s in range(lo, hi + 1):
            conflict = False
            for neighbor in adj[task_idx]:
                if current_assignment[neighbor] == s:
                    conflict = True
                    break
            if conflict:
                continue
                
            cap_ok = True
            for r in range(4):
                if slots_util[s][r] + resources[task_idx][r] > capacities[s][r] + 1e-9:
                    cap_ok = False
                    break
            if not cap_ok:
                continue
                
            current_assignment[task_idx] = s
            for r in range(4):
                slots_util[s][r] += resources[task_idx][r]
                
            backtrack(task_idx + 1)
            
            for r in range(4):
                slots_util[s][r] -= resources[task_idx][r]
            current_assignment[task_idx] = -1
            
    backtrack(0)
    t_end = time.perf_counter()
    runtime_ms = int((t_end - t_start) * 1000)
    
    if best_assignment is not None:
        return {
            'assignment': best_assignment,
            'penalty': best_penalty,
            'runtime_ms': runtime_ms,
            'feasible': True,
            'violation_reason': ""
        }
    else:
        return {
            'assignment': {},
            'penalty': -1.0,
            'runtime_ms': runtime_ms,
            'feasible': False,
            'violation_reason': "Brute force search proved no feasible assignment exists."
        }

def solve_heuristic(instance, max_states=30000):
    """
    Implements Priority-Weighted Resource-Aware DSATUR (PW-RAD) with bounded backtracking.
    """
    t_start = time.perf_counter()
    tasks = instance['tasks']
    conflicts = instance['conflicts']
    resources = instance['resources']
    capacities = instance['capacities']
    windows = instance['windows']
    weights = instance['weights']
    K = instance['K']
    n = len(tasks)
    
    adj = [[] for _ in range(n)]
    for i, j in conflicts:
        adj[i].append(j)
        adj[j].append(i)
        
    static_difficulty = []
    for i in range(n):
        lo, hi = windows[i]
        sla_tightness = 1.0 / (hi - lo + 1)
        conflict_deg = len(adj[i])
        res_ratio = sum(resources[i][r] / sum(capacities[s][r] for s in range(K)) * K for r in range(4)) / 4.0
        difficulty = weights[i] * (1.5 * conflict_deg + 3.0 * sla_tightness + 2.0 * res_ratio)
        static_difficulty.append(difficulty)
        
    assignment = [-1] * n
    slots_util = [[0.0] * 4 for _ in range(K)]
    states_visited = 0
    
    def get_saturation_and_select():
        best_task = -1
        max_sat = -1
        max_diff = -1.0
        
        for i in range(n):
            if assignment[i] != -1:
                continue
                
            lo, hi = windows[i]
            blocked_slots = 0
            for s in range(lo, hi + 1):
                conflicted = False
                for neighbor in adj[i]:
                    if assignment[neighbor] == s:
                        conflicted = True
                        break
                if conflicted:
                    blocked_slots += 1
                    continue
                res_ok = True
                for r in range(4):
                    if slots_util[s][r] + resources[i][r] > capacities[s][r] + 1e-9:
                        res_ok = False
                        break
                if not res_ok:
                    blocked_slots += 1
                    
            if blocked_slots > max_sat:
                max_sat = blocked_slots
                best_task = i
                max_diff = static_difficulty[i]
            elif blocked_slots == max_sat:
                if static_difficulty[i] > max_diff:
                    best_task = i
                    max_diff = static_difficulty[i]
                    
        return best_task

    def backtrack():
        nonlocal states_visited
        states_visited += 1
        if states_visited > max_states:
            return None
            
        task_idx = get_saturation_and_select()
        if task_idx == -1:
            return {tasks[i]: assignment[i] for i in range(n)}
            
        lo, hi = windows[task_idx]
        feasible_slots = []
        
        for s in range(lo, hi + 1):
            conflict = False
            for neighbor in adj[task_idx]:
                if assignment[neighbor] == s:
                    conflict = True
                    break
            if conflict:
                continue
                
            cap_ok = True
            for r in range(4):
                if slots_util[s][r] + resources[task_idx][r] > capacities[s][r] + 1e-9:
                    cap_ok = False
                    break
            if not cap_ok:
                continue
                
            cost = weights[task_idx] * s
            if hi > lo:
                cost += weights[task_idx] * (((s - lo) / (hi - lo)) ** 2)
            feasible_slots.append((cost, s))
            
        feasible_slots.sort(key=lambda x: x[0])
        
        for _, s in feasible_slots:
            assignment[task_idx] = s
            for r in range(4):
                slots_util[s][r] += resources[task_idx][r]
                
            result = backtrack()
            if result is not None:
                return result
                
            for r in range(4):
                slots_util[s][r] -= resources[task_idx][r]
            assignment[task_idx] = -1
            
        return None

    heuristic_assignment = backtrack()
    t_end = time.perf_counter()
    runtime_ms = int((t_end - t_start) * 1000)
    
    if heuristic_assignment is not None:
        penalty = compute_penalty(heuristic_assignment, instance)
        return {
            'assignment': heuristic_assignment,
            'penalty': penalty,
            'runtime_ms': runtime_ms,
            'feasible': True,
            'violation_reason': ""
        }
    else:
        reason = "State budget exceeded" if states_visited > max_states else "Search space exhausted; no feasible slot assignment satisfies constraints."
        return {
            'assignment': {},
            'penalty': -1.0,
            'runtime_ms': runtime_ms,
            'feasible': False,
            'violation_reason': reason
        }
