# Quantum Collapse Algorithm

A procedural generation algorithm that is implemented classically and implemented to run on a quantum computer

See docs/algorithm.pdf for implementation details of the general classical algorithm

See experiments/QuantumComputingImplementation.ipynb for quantum computing implementation. Follow setup instructions for expirements below to run notebook

There is a cli tool to run the algorithm. The algortihm currently works on any
number of dimensions but only images are currently supported for input and output on the cli.

Currently the cli only runs the Quantum Computing version on Quantum Computer simulators. Once I test the algorithm on actually quantum computres then I will implement a flag on the cli to choose to use simulator or real quantum computers

## Setup & Install
```
pip install -r requirements.txt
```

## Cli

```
--input INPUT --patch_size PATCH_SIZE --output_size OUTPUT_SIZE --output_file OUTPUT_FILE [--quantum_compute | --quantum_randomness] [--verbose]
```

```
optional arguments:
  -h, --help            show this help message and exit
  --input INPUT, -i INPUT
                        A local file path, file directory, or a url
  --patch_size PATCH_SIZE, --patchsize PATCH_SIZE
                        CSV of numbers that specifies size of input parts. Dimension must match input dimension
  --output_size OUTPUT_SIZE, --outputsize OUTPUT_SIZE
                        Size out the output. Dimension must match the input dimension
  --output_file OUTPUT_FILE, --f OUTPUT_FILE
                        Output file where generated output will be saved
  --quantum_compute, --qc
                        This flags enables running the quantum computing implementation of the quantum collapse algorithm using Grover's Search
  --quantum_randomness, --qr
                        This flags enables using quantum randomness through quantum computing
  --verbose, -v         Incremental verbose parameter. -v prints steps and elapsed time. -vv saves debug figures
```

## Experiments

### Setup
```
pip install jupyterlab
pip install pylatexenc
```
```
pip install -r requirements.txt
```