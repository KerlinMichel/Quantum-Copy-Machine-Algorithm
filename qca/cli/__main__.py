import argparse
import builtins
import math
import os
import time

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from qca import create_neighborhood, quantum_collapse, quantum_collapse_qc
from qca.collapse import BinaryCollapse
from qca.decoherence import LowestEntropyDechorence
from qca.input import create_patches, create_adjacency_matrix, parse_input, save_output

parser = argparse.ArgumentParser()

parser.add_argument('--input', '-i', type=str, required=True, help='A local file path, file directory, or a url')
parser.add_argument('--patch_size', '--patchsize', type=lambda s: tuple(map(int, s.split(','))), required=True, help='CSV of numbers that specifies size of input parts. Dimension must match input dimension')

parser.add_argument('--output_size', '--outputsize', type=lambda s: tuple(map(int, s.split(','))), required=True, help='Size out the output. Dimension must match the input dimension')
parser.add_argument('--output_file', '--f', type=str, required=True, help='Output file where generated output will be saved')

algorithm_mode_group = parser.add_mutually_exclusive_group(required=False)

algorithm_mode_group.add_argument('--quantum_compute', '--qc', required=False, action='store_true', help='This flags enables running the quantum computing implementation of the quantum collapse algorithm using Grover\'s Search')

algorithm_mode_group.add_argument('--quantum_randomness', '--qr', required=False, action='store_true', help='This flags enables using quantum randomness through quantum computing')

parser.add_argument('--verbose', '-v', action='count', default=0, required=False, help='Incremental verbose parameter. -v prints steps and elapsed time. -vv saves debug figures ')

args = parser.parse_args()

# print function will only print when verbose is set above zero
print = lambda *values: builtins.print(*values) if args.verbose > 0 else None

if os.path.isdir(args.input):
    input_type = None

    files = [os.path.join(args.input, f) for f in os.listdir(args.input)]
    patches = np.zeros((len(files)), dtype=object)

    for i, full_path in enumerate(files):
        input, input_type_i = parse_input(full_path)
        if input_type == None:
            input_type = input_type_i
        if input_type_i != input_type:
            raise ValueError('Folder contains more than one type of input')
        patches[i] = input
else:
    patches, input, input_type = create_patches(input=args.input, patch_size=args.patch_size)
    patches = patches.flatten()

if input_type == 'image' and len(args.patch_size) != 2:
    raise ValueError('Input is an image. Patch size must only contain 2 values.')

if input_type == 'image' and len(args.output_size) != 2:
    raise ValueError('Input is an image. Output size must only contain 2 values.')

print('input type: ' + input_type)

if input_type == 'image':
    num_dimensions = 2

neighborhood = create_neighborhood(num_dimensions=num_dimensions, neighborhood_type='manhattan_distance_1')

if args.verbose > 1:
    if input_type == 'image':
        states_img = Image.new('RGBA', (1000, 2000), 'white')
        states_img_draw = ImageDraw.Draw(states_img)
        font = ImageFont.load_default()
        i = 0
        for r in range(20):
            for c in range(10):
                if i >= len(patches):
                    break
                state = patches[i]
                state_name = str(i)
                state_size = f'{state.shape[1]}x{state.shape[0]}'

                states_img.paste(Image.fromarray(state), ((c*100) + 50 - state.shape[1]//2, (r*100) + 50 - state.shape[0]//2))

                states_img_draw.rectangle((c*100, r*100, (c+1)*100, (r+1)*100), outline='black')

                tw, th = states_img_draw.textsize(state_name, font=font)
                states_img_draw.text(((c*100) + 50 - tw//2, r*100), state_name, font=font, fill='black')

                sw, _ = states_img_draw.textsize(state_size, font=font)
                states_img_draw.text(((c*100) + 50 - sw//2, r*100 + th), state_size, font=font, fill='black')

                i += 1

        states_img.save('states.png')

start_time = time.time()
adjacency_matrix = create_adjacency_matrix(patches, neighborhood)

print(f'neighborhood matrix created ({time.time() - start_time:.4f} s)')

dechorence_selector = LowestEntropyDechorence()
collapse = BinaryCollapse()

if args.quantum_randomness:
    from qca.quantum_computing import choice
    dechorence_selector = LowestEntropyDechorence(choice=choice)
    collapse = BinaryCollapse(choice=choice)

start_time = time.time()
if args.quantum_compute:
    # define N as the state database size and M as the number of solutions
    # let use assume there is at least 1 solution (this isn't always true)
    # grovers algorithm expects to find a queried state after √(N/M)
    N = math.prod(args.output_size)**len(patches)
    M = 1
    num_iterations = math.ceil(math.sqrt(N/M))
    print('Iteration Count: ', num_iterations)

    success, output = quantum_collapse_qc(patches, output_size=args.output_size, neighborhood_constraint=adjacency_matrix, neighborhood=neighborhood,
                                          num_iterations=num_iterations)
else:
    success, output, _ = quantum_collapse(patches, output_size=args.output_size, adjacency_contraint=adjacency_matrix, neighborhood=neighborhood,
                                          dechorence_selector=dechorence_selector, collapse=collapse)

print(f'Done. success: {success} ({time.time() - start_time:.4f} s)')

if input_type == 'image':
    save_output(args.output_file, output, patches, 'image')