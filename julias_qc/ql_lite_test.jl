using Test

include("ql_lite.jl")

function bell_state_test()
    basis_states, create_null_state, parse_quantum_state = quantize([0, 1])

    quantum_state = create_null_state(2)
    @test !is_quantum_state(quantum_state)

    quantum_state[1] = 1.0+0im
    @test is_quantum_state(quantum_state)

    qc = quantum_compute(quantum_state).gate(H, I).gate(CNOT)

    expected_collapsedbell_state = [[1.0, 0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 1.0]]
    expected_bell_state_results = ["0.0,0.0,0.0,1.0,", "1.0,0.0,0.0,0.0,"]

    @test qc.collapse() in expected_collapsedbell_state

    sample = qc.sample(10)
    for res in keys(sample)
        @test res in expected_bell_state_results
    end
end

@testset "Basic QC Tests" begin
    bell_state_test()
end