
import pandas as pd
from causal_reasoning.linear_algorithm.scalable_problem import ScalarProblem, checkQuerry, single_exec
from causal_reasoning.utils.get_scalable_df import getScalableDataFrame
import time as tm

def main():
    df = pd.DataFrame(columns=['N','M','LOWER_BOUND','LOWER_BOUND_SECONDS_TAKEN','LOWER_BOUND_REQUIRED_ITERATIONS','UPPER_BOUND','UPPER_BOUND_SECONDS_TAKEN','UPPER_BOUND_REQUIRED_ITERATIONS','BOUNDS_SIZE', 'TRUE_PROBABILITY_VALUE'])
    df.to_csv("results.csv", index=False)
    M=1
    for N in range(1, 11):
        try:
            scalable_df = getScalableDataFrame(M=M, N=N)
            interventionValue = 1; targetValue = 1
            start = tm.time()
            scalarProblem = ScalarProblem.buildScalarProblem(M=M, N=N, interventionValue=interventionValue, targetValue=targetValue, df=scalable_df, minimum = True)
            lower , lower_iterations = scalarProblem.solve()
            end = tm.time()
            lower_time = end-start

            scalarProblem = ScalarProblem.buildScalarProblem(M=M, N=N, interventionValue=interventionValue, targetValue=targetValue, df=scalable_df, minimum = False)
            start = tm.time()
            upper, upper_iterations = scalarProblem.solve()
            end = tm.time()
            upper = -upper
            upper_time = end-start
            
            if (isinstance(lower, int) and isinstance(upper, int)) or (isinstance(lower, float) and isinstance(upper, float)):
                bounds_size = upper - lower
            else:
                bounds_size = None
            df = pd.read_csv("results.csv")
            new_row = {'N': N,'M': M,'LOWER_BOUND': lower,'LOWER_BOUND_SECONDS_TAKEN': lower_time,'LOWER_BOUND_REQUIRED_ITERATIONS': lower_iterations,'UPPER_BOUND': upper,'UPPER_BOUND_SECONDS_TAKEN': upper_time,'UPPER_BOUND_REQUIRED_ITERATIONS': upper_iterations,'BOUNDS_SIZE': bounds_size, 'TRUE_PROBABILITY_VALUE':checkQuerry(N,M,1,1)}
            new_row_df = pd.DataFrame([new_row])
            df = pd.concat([df, new_row_df], ignore_index=True)
            df.to_csv("results.csv", index=False)
        except Exception:
            pass

    for M in range(2, 7):
        for N in range(1, 7):
            try:
                scalable_df = getScalableDataFrame(M=M, N=N)
                interventionValue = 1; targetValue = 1
                start = tm.time()
                scalarProblem = ScalarProblem.buildScalarProblem(M=M, N=N, interventionValue=interventionValue, targetValue=targetValue, df=scalable_df, minimum = True)
                lower , lower_iterations = scalarProblem.solve()
                end = tm.time()
                lower_time = end-start

                scalarProblem = ScalarProblem.buildScalarProblem(M=M, N=N, interventionValue=interventionValue, targetValue=targetValue, df=scalable_df, minimum = False)
                start = tm.time()
                upper, upper_iterations = scalarProblem.solve()
                end = tm.time()
                upper = -upper
                upper_time = end-start
                
                if (isinstance(lower, int) and isinstance(upper, int)) or (isinstance(lower, float) and isinstance(upper, float)):
                    bounds_size = upper - lower
                else:
                    bounds_size = None
                df = pd.read_csv("results.csv")
                new_row = {'N': N,'M': M,'LOWER_BOUND': lower,'LOWER_BOUND_SECONDS_TAKEN': lower_time,'LOWER_BOUND_REQUIRED_ITERATIONS': lower_iterations,'UPPER_BOUND': upper,'UPPER_BOUND_SECONDS_TAKEN': upper_time,'UPPER_BOUND_REQUIRED_ITERATIONS': upper_iterations,'BOUNDS_SIZE': bounds_size, 'TRUE_PROBABILITY_VALUE':checkQuerry(N,M,1,1)}
                new_row_df = pd.DataFrame([new_row])
                df = pd.concat([df, new_row_df], ignore_index=True)
                df.to_csv("results.csv", index=False)
            except Exception:
                pass
    print("Done")

if __name__=="__main__":
    main()