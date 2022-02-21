from collections import deque
from typing import Tuple

import numpy as np

from .decoherence import LowestEntropyDechorence
from .collapse import BinaryCollapse

def quantum_collapse(
    states,
    output_size: Tuple[int, ...],
    neighborhood,
    adjacency_contraint,
    dechorence_selector=LowestEntropyDechorence,
    collapsor = BinaryCollapse,
):
    output = np.ones((output_size + (len(states),)))
    output_curr_num_possible_states = np.full((output_size), len(states), dtype=int)
    output_assignments = np.full((output_size), -1, dtype=int)

    dechorence_selector = dechorence_selector()
    collapse = collapsor()

    output_is_consistent = True

    while not np.all(output_assignments != -1) and output_is_consistent:
        collapsing_superposition = dechorence_selector(output, output_curr_num_possible_states, output_assignments)
        collapsed_index, _ = collapse(collapsing_superposition, output, output_curr_num_possible_states, output_assignments)
        propagation_queue = deque()

        propagation_queue.append(collapsed_index)

        # propagate updates through output
        while len(propagation_queue) > 0:
            index = propagation_queue.pop()

            for n_i, neighbor_vector in enumerate(neighborhood):
                neighbor_index = np.array(index) + np.array(neighbor_vector)

                # skip out of bounds indexes
                if np.any(neighbor_index < 0) or np.any(neighbor_index > np.array(output.shape[:-1]) - 1):
                    continue

                num_possible_states_before_update = output_curr_num_possible_states[tuple(neighbor_index)]

                for neighbor_state_idx, v in enumerate(output[tuple(neighbor_index)]):
                    if v == 0:
                        continue

                    # loop through output part that was popped to see if neighbor states are possible based on neighborhood constraint
                    state_is_possible = False
                    for state_index, v_ in enumerate(output[tuple(index)]):
                        if v_ == 0:
                            continue
                        if adjacency_contraint[state_index, n_i, neighbor_state_idx] == 1:
                            state_is_possible = True
                            break

                    if not state_is_possible:
                        output[tuple(neighbor_index)][neighbor_state_idx] = 0
                        output_curr_num_possible_states[tuple(neighbor_index)] -= 1

                # possible states are zero so output is not inconsistent
                if output_curr_num_possible_states[tuple(neighbor_index)] == 0:
                    output_is_consistent = False
                # if number of possible states has changed then propagate
                elif output_curr_num_possible_states[tuple(neighbor_index)] - num_possible_states_before_update != 0:
                    propagation_queue.append(neighbor_index)


    # collapse states that only have one possible state
    for i, v in np.ndenumerate(output_curr_num_possible_states):
        if v == 1 and output_assignments[i] == -1:
            value = np.argwhere(output[i] > 0)[0]
            output_assignments[i] = value

    return output_is_consistent, output_assignments, output

def create_neighborhood(num_dimensions, neighborhood_type='manhattan_distance_1'):
    if neighborhood_type == 'manhattan_distance_1':
        neighborhood = tuple([0] * num_dimensions for _ in range(num_dimensions * 2))
        for idx, i in enumerate(range(0, len(neighborhood), 2)):
            neighborhood[i][idx] = 1
            neighborhood[i+1][idx] = -1

        return neighborhood

def feasible_on_neighborhood_constraint(output_assignments, neighborhood_constraint, neighborhood):
    indices = np.ndindex(output_assignments.shape)

    for i in indices:
        for i_n, n in enumerate(neighborhood):
            state = output_assignments[i]
            neighbor_index = np.array(i)+np.array(n)

            if np.any(neighbor_index < 0) or np.any(neighbor_index > np.array(output_assignments.shape) - 1):
                    continue

            n_state = output_assignments[tuple(neighbor_index)]

            # ignore if assignment has not been made on the state or its neighbor
            if state == -1 or n_state == -1:
                continue

            if neighborhood_constraint[state, i_n, n_state] == 0:
                return False

    return True
