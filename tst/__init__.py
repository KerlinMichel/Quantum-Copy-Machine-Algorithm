import unittest

import numpy as np

from qca import feasible_on_neighborhood_constraint
from qca.input import create_neighborhood_constraint_from_example

def convert_to_state_index_assignment(states, input):
    input_assignments = np.zeros_like(input, dtype=int)
    for i, s in np.ndenumerate(input):
        input_assignments[i] = np.where(states == s)[0][0]
    return input_assignments

class FeasibleTest(unittest.TestCase):
    def test_1D(self):
        states = np.array(['🟥', '🟦'])
        input_example = np.array(list('🟥🟥🟦'))

        feasible_example_1 = np.array(list('🟥'))
        feasible_example_2 = np.array(list('🟥🟥🟥🟥🟥🟥🟥🟦'))

        infeasible_example_1 = np.array(list('🟥🟥🟦🟥'))
        infeasible_example_2 = np.array(list('🟦🟥'))

        neighborhood = [(1,)]

        c_n = create_neighborhood_constraint_from_example(states, input_example, neighborhood)

        # input example should always be feasible since neighborhood constraint is based on input example
        input_assignments = convert_to_state_index_assignment(states, input_example)
        feasible = feasible_on_neighborhood_constraint(input_assignments, c_n, neighborhood)
        self.assertTrue(feasible)

        for e in [feasible_example_1, feasible_example_2]:
            assignments = convert_to_state_index_assignment(states, e)
            feasible = feasible_on_neighborhood_constraint(assignments, c_n, neighborhood)
            self.assertTrue(feasible)

        for e in [infeasible_example_1, infeasible_example_2]:
            assignments = convert_to_state_index_assignment(states, e)
            feasible = feasible_on_neighborhood_constraint(assignments, c_n, neighborhood)
            self.assertFalse(feasible)

if __name__ == '__main__':
    unittest.main()