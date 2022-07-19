using LinearAlgebra

const QuantumState = Vector{<:Real}
const QuantumBasis = Vector{<:QuantumState}
const Qubit = QuantumState

qubit_states = [0, 1]

function quantize(basis_states::Vector)
    num_basis_states = length(basis_states)
    basis_states_ = basis_states
    basis_states = [[0. for _ = 1:num_basis_states] for _ = 1:num_basis_states]

    # create orthonormal basis
    for i in 1:length(basis_states)
        basis_states[i][i] = 1.
    end

    function parse_quantum_state(quantum_state, join_=false)
        num_b_states = log(num_basis_states, length(quantum_state))
        if (num_basis_states ^ num_b_states) ≠ length(quantum_state)
            throw(ErrorException("Invalid quantum state"))
        end

        num_b_states = floor(Int, num_b_states)

        result = Array{typeof(basis_states_[1]), 1}(undef, num_b_states)

        for i in 1:length(quantum_state)
            if quantum_state[i] == 1.
                digits_ = digits(i-1, base = num_basis_states, pad = num_b_states)

                for (d_idx, digit) in enumerate(digits_)
                    result[d_idx] = basis_states_[digit+1]
                end

                if join_
                    return join(result)
                end

                return result
            end
        end

        throw(ErrorException("Parse fail"))
    end

    # create a quantum state with the value set to 0, an invalid null state
    function create_null_state(num_q_objects::Int)
        return [0.0+0im for _ = 1:length(basis_states) ^ num_q_objects]
    end

    return basis_states, create_null_state, parse_quantum_state
end

function collapse_quantum_state(quantum_state)
    sum = 0
    cum_sum = []
    for i in quantum_state
        append!(cum_sum, sum)

        # use magnitude of squaring the imaginary numbers to get probabilty (born's rule)
        sum += abs(i*i)
    end

    select = rand() * sum

    for i in 1:length(cum_sum)
        j = (length(quantum_state)+1) - i
        if select >= cum_sum[j]
            quantum_state = [0. for _ = 1:length(quantum_state)]
            quantum_state[j] = 1.0
            return quantum_state
        end
    end

    throw(ErrorException("Failed to collapse state"))
end

function sample_quantum_state(quantum_state, n)
    results = Dict()
    for _ in 1:n
        result = collapse_quantum_state(quantum_state)
        res_str = ""
        for e in result
            res_str *= string(e, ",")
        end
        if haskey(results, res_str)
            results[res_str] += 1 
        else
            results[res_str] = 1 
        end
    end

    return results
end

function is_quantum_state(quantum_state)
    return typeof(quantum_state).parameters[1] <: Complex && norm(quantum_state) == 1
end

function create_gate(qc)
    return function gate_(gates...)
        num_dimensions = length(qc.quantum_state)
        gate_builder = gates[1]

        for i in 2:length(gates)
            gate_builder = gate_builder ⊗ gates[i]
        end

        n, m = size(gate_builder)

        if !(num_dimensions == n == m)
            throw(ErrorException("invalid gate"))
        end

        qc.quantum_state = gate_builder * qc.quantum_state
        return qc
    end
end

mutable struct QuantumComputer
    quantum_state
    gate
    collapse
    sample
    self

    QuantumComputer(quantum_state) = (qc = new(quantum_state);
                                      qc.gate = create_gate(qc);
                                      qc.collapse = () -> collapse_quantum_state(qc.quantum_state);
                                      qc.sample = (n) -> sample_quantum_state(qc.quantum_state, n);
                                      qc.self = qc;)
end

function quantum_compute(quantum_state)
    return QuantumComputer(quantum_state)
end

⊗(a, b) = kron(a, b)

const I = [1.0+0im   0.0+0im
           0.0+0im   1.0+0im]

const H = [1/√2+0im   1/√2+0im
           1/√2+0im  -1/√2+0im]

const Z = [1.0+0im   0.0+0im
           0.0+0im  -1.0+0im]

const X = [0.0+0im   1.0+0im
           1.0+0im   0.0+0im]

const CNOT = [1.0+0im   0.0+0im   0.0+0im   0.0+0im
              0.0+0im   1.0+0im   0.0+0im   0.0+0im
              0.0+0im   0.0+0im   0.0+0im   1.0+0im
              0.0+0im   0.0+0im   1.0+0im   0.0+0im]

function phase(theta)
    theta = deg2rad(theta)
   return [1.0+0im   0.0+0im
           0.0+0im   ℯ ^ (1im*theta)]
end

const P = phase
const P_90 = phase(90)