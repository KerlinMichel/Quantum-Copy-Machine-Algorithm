# Quantum Collapse Algorithm

See docs/algorithm.pdf for implementation details

## Setup & Install
```
pip install -r requirements.txt
```

## Cli

```
python -m qca.cli  [-h] --input INPUT --patch_size PATCH_SIZE --output_size OUTPUT_SIZE --output_file OUTPUT_FILE [--quantum_randomness]
```

```
optional arguments:
  -h, --help            show this help message and exit
  --input INPUT, -i INPUT
                        A local file path or a url
  --patch_size PATCH_SIZE, --patchsize PATCH_SIZE
                        CSV of numbers that specifies size of input parts. Dimension must match input dimension
  --output_size OUTPUT_SIZE, --outputsize OUTPUT_SIZE
                        Size out the output. Dimension must match the input dimension
  --output_file OUTPUT_FILE, --f OUTPUT_FILE
                        Output file where generated output will be saved
  --quantum_randomness, --qr
                        This flags enables using quantum randomness through quantum computing
```