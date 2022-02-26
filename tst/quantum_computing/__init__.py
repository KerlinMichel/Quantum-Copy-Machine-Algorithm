import unittest

from qca.quantum_computing import get_circuit_statevector, build_random_integer_circuit

class StateVectorTest(unittest.TestCase):

    def test_get_circuit_statevector(self):
        random_int_circuit = build_random_integer_circuit(8)

        state_vector = get_circuit_statevector(random_int_circuit)

        # states should be equally probable
        self.assertTrue(len(set(state_vector.data)) == 1)

if __name__ == '__main__':
    unittest.main()