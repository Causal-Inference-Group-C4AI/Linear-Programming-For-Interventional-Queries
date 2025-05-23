
import pandas as pd
from causal_reasoning.linear_algorithm.scalable_problem import ScalarProblem, checkQuerry, single_exec
from causal_reasoning.utils.get_scalable_df import getScalableDataFrame
import time as tm

def main():
    df = pd.DataFrame(columns=['N','M','LOWER_BOUND','LOWER_BOUND_REQUIRED_ITERATIONS','UPPER_BOUND','TOTAL_SECONDS_TAKEN','UPPER_BOUND_REQUIRED_ITERATIONS','BOUNDS_SIZE'])
    df.to_csv("./outputs/results_1.csv", index=False)
    N_M = [
            #(1,1),
            #(2,1),
            #(3,1),
            #(4,1),
            #(5,1),
            #(1,2),
            #(2,2),
            (3,2)]#,
            #(4,2),
            #(1,3),
            #(2,3),
            #(3,3)]
    for values in N_M:
        N, M = values
        try:
            scalable_df = getScalableDataFrame(M=M, N=N)
            interventionValue = 1; targetValue = 1
            start = tm.time()
            scalarProblem = ScalarProblem.buildScalarProblem(M=M, N=N, interventionValue=interventionValue, targetValue=targetValue, df=scalable_df, minimum = True)
            lower , lower_iterations = scalarProblem.solve()

            scalarProblem = ScalarProblem.buildScalarProblem(M=M, N=N, interventionValue=interventionValue, targetValue=targetValue, df=scalable_df, minimum = False)
            upper, upper_iterations = scalarProblem.solve()
            end = tm.time()
            upper = -upper
            upper_time = end-start
            
            if (isinstance(lower, int) and isinstance(upper, int)) or (isinstance(lower, float) and isinstance(upper, float)):
                bounds_size = upper - lower
            else:
                bounds_size = None
            df = pd.read_csv("./outputs/results_1.csv")
            new_row = {'N': N,'M': M,'LOWER_BOUND': lower,'LOWER_BOUND_REQUIRED_ITERATIONS': lower_iterations,'UPPER_BOUND': upper,'TOTAL_SECONDS_TAKEN': upper_time,'UPPER_BOUND_REQUIRED_ITERATIONS': upper_iterations,'BOUNDS_SIZE': bounds_size}
            new_row_df = pd.DataFrame([new_row])
            df = pd.concat([df, new_row_df], ignore_index=True)
            df.to_csv("./outputs/results_1.csv", index=False)
        except Exception:
            pass
    print("Done")

if __name__=="__main__":
    main()