
import pandas as pd
from causal_reasoning.linear_algorithm.scalable_problem import ScalarProblem, checkQuerry, single_exec
from causal_reasoning.utils.get_scalable_df import getScalableDataFrame
import time as tm

def main():
    df = pd.DataFrame(columns=['N','M','LOWER_BOUND','LOWER_BOUND_REQUIRED_ITERATIONS','UPPER_BOUND','UPPER_BOUND_REQUIRED_ITERATIONS', 'TOTAL_SECONDS_TAKEN'])
    df.to_csv("./outputs/gc_results.csv", index=False)
    N_M = [
            (1,1),
            (2,1),
            (3,1),
            (4,1),
            (5,1),
            (6,1),
            (1,2),
            (2,2),
            (3,2),
            (4,2),
            (1,3),
            (2,3),
            (3,3),
            (4,3),
    ]
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
            total_time = end-start

            df = pd.read_csv("./outputs/gc_results.csv")
            new_row = {'N': N,'M': M,'LOWER_BOUND': lower,'LOWER_BOUND_REQUIRED_ITERATIONS': lower_iterations,'UPPER_BOUND': upper,'UPPER_BOUND_REQUIRED_ITERATIONS': upper_iterations, 'TOTAL_SECONDS_TAKEN':total_time}
            new_row_df = pd.DataFrame([new_row])
            df = pd.concat([df, new_row_df], ignore_index=True)
            df.to_csv("./outputs/gc_results.csv", index=False)
        except Exception as e:
            with open("./outputs/gc_error_log.txt", 'a') as file:
                file.write(f"Error: {e}")
            df = pd.read_csv("./outputs/gc_results.csv")
            new_row = {'N': N,'M': M,'LOWER_BOUND': None,'LOWER_BOUND_REQUIRED_ITERATIONS': None,'UPPER_BOUND': None,'UPPER_BOUND_REQUIRED_ITERATIONS': None, 'TOTAL_SECONDS_TAKEN':None}
            new_row_df = pd.DataFrame([new_row])
            df = pd.concat([df, new_row_df], ignore_index=True)
            df.to_csv("./outputs/gc_results.csv", index=False)
            pass
    print("Done")

if __name__=="__main__":
    main()