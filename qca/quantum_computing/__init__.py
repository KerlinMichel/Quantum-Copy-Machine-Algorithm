import math

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, Aer, BasicAer, assemble, execute
from qiskit.quantum_info import Statevector

def build_random_integer_circuit(num_bits):
    q = QuantumRegister(num_bits, 'q')
    c = ClassicalRegister(num_bits, 'c')
    circuit = QuantumCircuit(q, c)

    # Apply hadamard gate to put all qubits in balanced superposition
    circuit.h(q)
    circuit.measure(q, c)

    return circuit

def get_circuit_statevector(circuit: QuantumCircuit):
    # Statevector.from_instruction doesn't work if the circuit has measure gates
    for i in range(len(circuit.data) - 1, -1, -1):
        if circuit.data[i][0].name == 'measure':
            circuit.data.pop(i)

    state = Statevector.from_instruction(circuit)
    return state

def choice(iter, sim=Aer.get_backend('aer_simulator')):
    num_states = len(iter)

    # iterable only has one possible state
    if num_states == 1:
        return iter[0]

    num_bits = int(math.log2(num_states- 1)) + 1
    choice_index = -1

    random_int_circuit = build_random_integer_circuit(num_bits=num_bits)

    while choice_index < 0 or choice_index >= len(iter):
        result = sim.run(random_int_circuit, shots=1).result()
        counts = result.results[0].data.counts

        # results are stored by counting which state the circuit collapses to
        hex_value = list(counts.keys())[0]

        # states are represented in hex
        choice_index = int(hex_value, 16)

    return iter[choice_index]
