import numpy as np
import random as rand
def distribution(cardinalities : list[int], prec = 3):
    probs = np.empty(len(cardinalities), dtype = object)

    for j, card in enumerate(cardinalities):
        dist = np.empty(card)
        for i in range(dist.size):
            dist[i] = rand.uniform(1,100)
        dist = dist/np.sum(dist)
        dist = np.trunc(dist*10**prec)/10**prec
        dist[-1] = 1 - np.sum(dist[0:card-1])        
        probs[j] = dist

    return probs


        