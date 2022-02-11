from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, BasicAer, execute
import math

def random_integer(num_bits):
    q = QuantumRegister(num_bits, 'q')
    c = ClassicalRegister(num_bits, 'c')
    circuit = QuantumCircuit(q, c)
    # Apply hadamard gate to put all qubits in 50/50 superposition
    circuit.h(q)
    circuit.measure(q, c)

    backend = BasicAer.get_backend('qasm_simulator')

    job = execute(circuit, backend, shots=1, memory=True)
                                      
    result = job.result()

    return int(result.get_memory()[0], 2)

def choice(iter):
    num_bits = math.ceil(math.log2(len(iter)))
    choice_index = -1

    while choice_index < 0 or choice_index >= len(iter):
        choice_index = random_integer(num_bits=num_bits)

    return iter[choice_index]
