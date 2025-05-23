import pandas as pd
import time as tm
from causal_reasoning.utils._enum import Examples
from causal_reasoning.causal_model import CausalModel
from causal_reasoning.utils.get_scalable_df import getScalableDataFrame

def genGraph(N, M):
    scalable_input: str = "U1 -> X, U3 -> Y, "
    for i in range(1,N + 1):
        scalable_input += f"U1 -> A{i}, "
        if (i == 1):
            scalable_input += "X -> A1, "
        else:
            scalable_input += f"A{i-1} -> A{i}, "
    scalable_input += f"A{N} -> Y, "

    for i in range(1,M + 1):
        scalable_input += f"U2 -> B{i}, "
        scalable_input += f"X -> B{i}, "
        for j in range(1,N + 1):
            scalable_input += f"B{i} -> A{j}, "
            
    return scalable_input[:-2]


def main():
    N = 1; M = 1
    df = pd.DataFrame(columns=['N','M','LOWER_BOUND','UPPER_BOUND','BOUNDS_SECONDS_TAKEN','BOUNDS_SIZE'])
    df.to_csv("./outputs/algorithm_results.csv", index=False)

    scalable_unobs = ["U1", "U2", "U3"]
    scalable_target = "Y"; target_value = 1
    scalable_intervention = "X"; intervention_value = 1    

    N_M = [
        # (1,1),
        #     (2,1),
            #(3,1)
            # (4,1),
            # (5,1),
            # (1,2),
            # (2,2),
            # (3,2),
            # (4,2),
            # (1,3),
            (2,3)
            # (3,3)
            ]
    for n_m in N_M:
        N, M = n_m
        scalable_input = genGraph(N, M)    
        scalable_df = getScalableDataFrame(M=M, N=N)
        print("starting")
        scalable_model = CausalModel(
            data=scalable_df,
            edges=scalable_input,
            unobservables=scalable_unobs,
            interventions=scalable_intervention,
            interventions_value=intervention_value,
            target=scalable_target,
            target_value=target_value,
        )

        lower, upper = scalable_model.inference_query(gurobi=True)
        print(lower)
        print(upper)

    
    print("Done")

if __name__ == "__main__":
    main()
