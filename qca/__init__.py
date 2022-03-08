from collections import deque
from itertools import zip_longest
from typing import Tuple

import numpy as np
from qiskit import Aer, transpile, assemble

from .decoherence import LowestEntropyDechorence
from .collapse import BinaryCollapse
from .quantum_computing import *

def quantum_collapse(
    states,
    output_size: Tuple[int, ...],
    neighborhood,
    adjacency_contraint,
    dechorence_selector=LowestEntropyDechorence(),
    collapse = BinaryCollapse(),
):
    output = np.ones((output_size + (len(states),)))
    output_curr_num_possible_states = np.full((output_size), len(states), dtype=int)
    output_assignments = np.full((output_size), -1, dtype=int)

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

def quantum_collapse_qc(
    states,
    output_size: Tuple[int, ...],
    neighborhood,
    neighborhood_constraint,
    num_iterations=1,
    max_attempts=1,
    sim=Aer.get_backend('aer_simulator')
):
    output = np.ones(output_size + (len(states),))
    output_assignments = np.full((output_size), -1, dtype=int)
    circuit, (output_qrs, output_part_qr_mapping), (neighborhood_constraint_qrs, neighborhood_constraint_output_mapping), feasible_qr = build_quantum_collapse_algorithm_circuit(states, neighborhood, output)

    set_quantum_collapse_algorithm_superposition(circuit, output_qrs)

    qc_grover = build_quantum_collapse_grover_search_circuit(circuit, neighborhood_constraint, output_qrs, neighborhood_constraint_qrs, neighborhood_constraint_output_mapping, num_iterations=num_iterations, to_gate=True)

    circuit.append(qc_grover, circuit.qubits)

    cbits = ClassicalRegister(len(output_qrs) * output_qrs[0].size, name='cbits')

    circuit.add_register(cbits)

    circuit.measure(flatten([qubits for qubits in output_qrs]), cbits._bits)

    for _ in range(max_attempts):
        transpiled_qc = transpile(circuit, sim)
        qobj = assemble(transpiled_qc)
        result = sim.run(qobj, shots=1).result()

        counts = result.get_counts()
        value_str = list(counts.keys())[0]

        # if hex string then convert to binary string
        if 'x' in value_str:
            value = int(value_str, 16)
            value_str = ''.join(str(i) for i in to_binary(value, num_bits=8))

        num_bits_per_state = int(len(value_str) / len(output_part_qr_mapping))

        bit_group_iter = list(grouper(num_bits_per_state, value_str))
        bit_group_iter = reversed(bit_group_iter)

        for oqr_i, bits in enumerate(bit_group_iter):
            bit_str = ''.join(bits)
            state = int(bit_str, 2)

            output_assignments[output_part_qr_mapping[oqr_i]] = state

        feasible = feasible_on_neighborhood_constraint(output_assignments, neighborhood_constraint, neighborhood)
        if feasible:
            break

    return feasible, output_assignments

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

# example: grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx
def grouper(n, iterable, fillvalue=None):
    args = [iter(iterable)] * n
    return zip_longest(fillvalue=fillvalue, *args)
