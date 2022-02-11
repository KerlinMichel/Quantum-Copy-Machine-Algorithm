from collections import deque
from typing import Tuple

import numpy as np

from .decoherence import LowestEntropyDechorence
from .collapse import BinaryCollapse

def quantum_collapse(
    states,
    output_size: Tuple[int, ...],
    neighborhood,
    adjacency_contraint
):
    output = np.ones((output_size + (len(states),)))
    output_curr_num_possible_states = np.full((output_size), len(states), dtype=int)
    reverse_neighborhood_ = tuple(neighborhood.index([-n for n in nh]) for nh in neighborhood)
    output_assignments = np.full((output_size), -1, dtype=int)

    dechorence_selector = LowestEntropyDechorence()
    collapse = BinaryCollapse()

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

                for idx, v in enumerate(output[tuple(neighbor_index)]):
                    if v == 0:
                        continue
                    # get all possible states based on adjacency_contraint
                    possible_states = np.where(adjacency_contraint[idx, reverse_neighborhood_[n_i]] > 0)[0]
                    
                    # check to see if current possible states are possible
                    v_possible = False
                    for s in possible_states:
                        if output[tuple(index)][s] > 0:
                            v_possible = True
                        
                    if not v_possible:
                        output[tuple(neighbor_index)][idx] = 0
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

def create_neighborhood(patches_shape, neighborhood_type='manhattan_distance_1'):
    if neighborhood_type == 'manhattan_distance_1':
        neighborhood = tuple([0] * len(patches_shape) for _ in range(len(patches_shape) * 2) )
        for idx, i in enumerate(range(0, len(neighborhood), 2)):
            neighborhood[i][idx] = 1
            neighborhood[i+1][idx] = -1

        return neighborhood
