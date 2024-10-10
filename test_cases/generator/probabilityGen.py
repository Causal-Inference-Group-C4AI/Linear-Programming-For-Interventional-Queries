import numpy as np
import random as rand
def distribution(cardinalities : list[int], prec = 3):
    probs = np.empty(cardinalities.size, dtype = object)
    j = 0
    for card in cardinalities:
        dist = np.empty(card)
        for i in range(dist.size):
            dist[i] = rand.uniform(1,100)
        dist = dist/np.sum(dist)
        dist = np.trunc(dist*10**prec)/10**prec
        dist[-1] = 1 - np.sum(dist[0:card-1])
        probs[j] = dist
        j+=1
    return probs
probs = distribution(np.array([1,2,3]))
print(probs)
print(probs[1][1])
        