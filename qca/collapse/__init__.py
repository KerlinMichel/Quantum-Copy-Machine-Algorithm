from typing import Any

import numpy as np
import numpy.random as random

choice = random.choice

class BinaryCollapse():
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.collapse(*args, **kwds)
    
    def collapse(self, index, output, output_curr_num_possible_states, output_assignments):
        output_curr_num_possible_states[index] = 1
        
        indices = np.where(output[index] == 1)[0]

        collapse_index = choice(indices)

        collapse_value = np.zeros(output.shape[-1])
        collapse_value[collapse_index] = 1
        output[index] = collapse_value

        output_assignments[index] = collapse_index

        return index, collapse_index