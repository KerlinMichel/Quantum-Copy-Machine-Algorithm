from typing import Tuple
from urllib.request import urlopen

import numpy as np
from PIL import Image

def parse_image(input: str):
     if type(input) is str:
        try:
            # if the input str is a url to an image then try to download it
            try:
                input = urlopen(input)
            except:
                pass
            return np.array(Image.open(input).convert('RGBA'))
        except Exception as e:
            raise e

def parse_input(input: str):
    for parser, input_type in [(parse_image, 'image')]:
        try:
            return parser(input), input_type
        except:
            raise ValueError('Could not parse image')


def create_patches(input, patch_size: Tuple[int, ...]):
    input, input_type = parse_input(input)

    patches_num_dimensions = None
    if input_type == 'image':
        patches_num_dimensions = 2

    patches = np.zeros(tuple(input.shape[i] // patch_size[i] for i in range(patches_num_dimensions)), dtype=object)
    
    for index, _ in np.ndenumerate(patches):
        patch_size = np.array(patch_size)
        index = np.array(index)

        patch = None

        # vector multiply index and patch size so we can index on the input
        # create patch by iterively taking from the numpy array on each axis
        for idx, i in np.ndenumerate(np.multiply(index, patch_size)):
            if patch is None:
                patch = np.take(input, range(int(i), int(i) + int(patch_size[idx[0]])), axis=idx[0])
            else:
                patch = np.take(patch, range(int(i), int(i) + int(patch_size[idx[0]])), axis=idx[0])

        patches[tuple(index)] = patch
    
    return patches, input, input_type

def create_adjacency_matrix(patches, neighborhood, type_='overlapping_boundaries'):
    adjacency_matrix = np.zeros((patches.shape + (len(neighborhood),) + patches.shape))

    for index1, patch1 in np.ndenumerate(patches):
        for index2, patch2 in np.ndenumerate(patches):
            if type_== 'overlapping_boundaries':
                for n_idx, n in enumerate(neighborhood):
                    # axis to get boundary
                    try:
                        axis = n.index(1)
                        direction = 1
                    except:
                        axis = n.index(-1)
                        direction = -1
    
                    # check if boundaries matched based on direction
                    if direction == 1:
                        overlaps = np.array_equal(np.take(patch1, [patch1.shape[axis]-1], axis=axis), np.take(patch2, [0], axis=axis))
                    elif direction == -1:
                        overlaps = np.array_equal(np.take(patch1, [0], axis=axis), np.take(patch2, [patch2.shape[axis]-1], axis=axis))

                    adjacency_matrix[index1+(n_idx,)+index2] = int(overlaps)

            else:
                raise ValueError('invalid type_')

    return adjacency_matrix

def create_neighborhood_constraint_from_example(states, example, neighborhood):
    neighborhood_constraint = np.zeros((len(states), len(neighborhood), len(states)))

    for idx, s in np.ndenumerate(example):
        for n_idx, n in enumerate(neighborhood):
            neighbor_index = np.array(idx)+np.array(n)

            if np.any(neighbor_index < 0) or np.any(neighbor_index > np.array(example.shape) - 1):
                    continue

            neighbor_state = example[tuple(neighbor_index)]

            neighborhood_constraint[np.where(states == s)[0][0], n_idx, np.where(states == neighbor_state)[0][0]] = 1

    return neighborhood_constraint

def save_output(file_path, output, patches, input_type):
    if input_type == 'image':
        img = Image.new("RGBA", tuple(np.array(patches[0].shape[:2]) * np.array(output.shape)))

        for r in range(output.shape[0]):
            for c in range(output.shape[1]):
                if output[r][c] != -1:
                    img.paste(Image.fromarray(patches[output[r][c]]), (c*patches[0].shape[1], r*patches[0].shape[0], (c+1)*patches[0].shape[1], (r+1)*patches[0].shape[0]))
        img.save(file_path)