import argparse

from qca.input import create_patches, create_adjacency_matrix, save_output
from qca.quantum_collapse import create_neighborhood, quantum_collapse

parser = argparse.ArgumentParser()

parser.add_argument('--input', '-i', type=str, required=True, help='A local file path or a url')
parser.add_argument('--patch_size', '--patchsize', type=lambda s: tuple(map(int, s.split(','))), required=True, help='CSV of numbers that specifies size of input parts. Dimension must match input dimension')

parser.add_argument('--output_size', '--outputsize', type=lambda s: tuple(map(int, s.split(','))), required=True, help='Size out the output. Dimension must match the input dimension')
parser.add_argument('--output_file', '--f', type=str, required=True, help='Output file where generated output will be saved')

parser.add_argument('--quantum_randomness', '--qr', required=False, action='store_true', help='This flags enables using quantum randomness through quantum computing')

args = parser.parse_args()

if args.quantum_randomness:
    from qca.quantum_computing import choice
    import qca.collapse
    qca.collapse.choice = choice
    import qca.decoherence
    qca.decoherence.choice = choice

patches, input, input_type = create_patches(input=args.input, patch_size=args.patch_size)

if input_type == 'image' and len(args.patch_size) != 2:
    raise ValueError('Input is an image. Patch size must only contain 2 values.')

if input_type == 'image' and len(args.output_size) != 2:
    raise ValueError('Input is an image. Output size must only contain 2 values.')

print('input type: ' + input_type)

neighborhood = create_neighborhood(patches_shape=patches.shape, neighborhood_type='manhattan_distance_1')

patches_ = patches
patches = patches.flatten()

adjacency_matrix = create_adjacency_matrix(patches, neighborhood)

print('adjacency matrix created')

success, output, _ = quantum_collapse(patches, output_size=args.output_size, adjacency_contraint=adjacency_matrix, neighborhood=neighborhood)

if input_type == 'image':
    save_output(args.output_file, output, patches, 'image')