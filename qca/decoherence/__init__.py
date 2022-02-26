import random
from typing import Any

import numpy as np

choice = random.choice

class LowestEntropyDechorence():
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.select(*args, **kwds)

    def select(self, output, output_curr_num_possible_states, output_assignments, choose_random=True):
        arg_min = np.inf

        lowest_entropies = []
        for i in np.ndindex(output.shape[:len(output.shape)-1]):
            if output_assignments[i] != -1:
                continue
            if 0 < output_curr_num_possible_states[i] < arg_min:
                arg_min = output_curr_num_possible_states[i]
                lowest_entropies = [i]
            elif output_curr_num_possible_states[i] == arg_min:
                lowest_entropies.append(i)

        if len(lowest_entropies) == 1:
            return lowest_entropies[0]
        else:
            if choose_random:
                return choice(lowest_entropies)
            else:
                raise Exception('Equal number of states')