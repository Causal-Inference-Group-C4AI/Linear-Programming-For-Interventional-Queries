import pandas as pd
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
    df = pd.DataFrame(columns=['N','M','LOWER_BOUND','LOWER_BOUND_SECONDS_TAKEN','UPPER_BOUND','UPPER_BOUND_SECONDS_TAKEN','BOUNDS_SIZE'])
    df.to_csv("algorithm_results.csv", index=False)

    scalable_unobs = ["U1", "U2", "U3"]
    scalable_target = "Y"; target_value = 1
    scalable_intervention = "X"; intervention_value = 1    

    #print("------")

    N_M = [(1,1),
            (2,1),
            (3,1),
            (4,1),
            (5,1),
            (1,2),
            (2,2),
            (3,2),
            (4,2),
            (1,3),
            (2,3),
            (3,3)]
    for n_m in N_M:
        N, M = n_m
        scalable_input = genGraph(N, M)    
        scalable_df = getScalableDataFrame(M=M, N=N)
        try:
            scalable_model = CausalModel(
                data=scalable_df,
                edges=scalable_input,
                unobservables=scalable_unobs,
                interventions=scalable_intervention,
                interventions_value=intervention_value,
                target=scalable_target,
                target_value=target_value,
            )

            lower, upper, lower_time, upper_time = scalable_model.inference_query(gurobi=True)
            df = pd.read_csv("algorithm_results.csv")
            bounds_size = upper - lower
            new_row = {'N': N,'M': M,'LOWER_BOUND': lower,'LOWER_BOUND_SECONDS_TAKEN': lower_time,'UPPER_BOUND': upper,'UPPER_BOUND_SECONDS_TAKEN': upper_time,'BOUNDS_SIZE': bounds_size}
            new_row_df = pd.DataFrame([new_row])
            df = pd.concat([df, new_row_df], ignore_index=True)
            df.to_csv("algorithm_results.csv", index=False)
        except Exception:
            pass


if __name__ == "__main__":
    main()
