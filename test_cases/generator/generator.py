from partition_methods.relaxed_problem.python import canonicalPartitions

def test():    
    adjRelaxed, unobRelaxed, unobCard = canonicalPartitions.completeRelaxed()

    print(f"Relaxed graph edges: {adjRelaxed} \n \nUnobservable variables: {unobRelaxed} \n \nCardinalities: {unobCard}")    

if __name__ == "__main__":
    test()