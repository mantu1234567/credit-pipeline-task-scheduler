import unittest
from solver import solve_heuristic, check_feasibility

class TestSchedulerSolver(unittest.TestCase):
    
    def test_single_task_instance(self):
        """
        Tests scheduling a single task.
        """
        instance = {
            'tasks': ['T0'],
            'conflicts': [],
            'resources': [[1.0, 1.0, 1.0, 1.0]],
            'capacities': [[32, 128, 8, 6.0], [32, 128, 8, 6.0]],
            'windows': [(0, 1)],
            'weights': [5.0],
            'K': 2
        }
        res = solve_heuristic(instance)
        self.assertTrue(res['feasible'], f"Failed single-task feasibility: {res['violation_reason']}")
        self.assertEqual(res['assignment']['T0'], 0, "Single task should be scheduled in slot 0 to minimize penalty")

    def test_all_conflict_graph(self):
        """
        Tests an all-conflict graph (fully connected graph K_3) with K = 2 slots.
        """
        instance = {
            'tasks': ['T0', 'T1', 'T2'],
            'conflicts': [(0, 1), (0, 2), (1, 2)], # K_3 graph
            'resources': [[1.0, 1.0, 1.0, 1.0]] * 3,
            'capacities': [[32, 128, 8, 6.0]] * 2,
            'windows': [(0, 1)] * 3,
            'weights': [1.0, 1.0, 1.0],
            'K': 2
        }
        res = solve_heuristic(instance)
        self.assertFalse(res['feasible'], "Should be infeasible due to chromatic number > K")

    def test_zero_capacity_slot(self):
        """
        Tests when one slot has zero capacity.
        """
        # Slot 0 has zero capacity, Slot 1 has capacity
        instance = {
            'tasks': ['T0'],
            'conflicts': [],
            'resources': [[2.0, 4.0, 1.0, 0.5]],
            'capacities': [[0, 0, 0, 0], [32, 128, 8, 6.0]],
            'windows': [(0, 1)],
            'weights': [1.0],
            'K': 2
        }
        res = solve_heuristic(instance)
        self.assertTrue(res['feasible'], "Should find a feasible assignment in slot 1")
        self.assertEqual(res['assignment']['T0'], 1, "Task should be scheduled in slot 1 because slot 0 has zero capacity")

        # Now force the SLA to ONLY slot 0, making it infeasible
        instance['windows'] = [(0, 0)]
        res_forced = solve_heuristic(instance)
        self.assertFalse(res_forced['feasible'], "Should be infeasible when forced to zero-capacity slot 0")

    def test_tight_sla_windows(self):
        """
        Tests a tight SLA scenario. Two tasks must run in slot 0, but they conflict.
        """
        instance = {
            'tasks': ['T0', 'T1'],
            'conflicts': [(0, 1)],
            'resources': [[1.0, 1.0, 1.0, 1.0]] * 2,
            'capacities': [[32, 128, 8, 6.0]] * 2,
            'windows': [(0, 0), (0, 0)], # Both forced to slot 0
            'weights': [1.0, 1.0],
            'K': 2
        }
        res = solve_heuristic(instance)
        self.assertFalse(res['feasible'], "Should be infeasible because conflicting tasks share tight [0, 0] window")

if __name__ == '__main__':
    unittest.main()
