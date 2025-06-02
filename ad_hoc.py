
import time as tm
import logging

logger = logging.getLogger(__name__)

import pandas as pd
from causal_reasoning.linear_algorithm.scalable_problem import ScalarProblem, checkQuerry, single_exec
from causal_reasoning.utils.get_scalable_df import getScalableDataFrame

def main():
    logging.basicConfig(level=logging.INFO)

    df = pd.DataFrame(columns=['N','M','LOWER_BOUND','LOWER_BOUND_REQUIRED_ITERATIONS','UPPER_BOUND','UPPER_BOUND_REQUIRED_ITERATIONS', 'TOTAL_SECONDS_TAKEN'])
    df.to_csv("./outputs/ad_hoc_results.csv", index=False)
    N_M = [
            (1,4)
    ]
    for values in N_M:
        N, M = values
        logger.info(f"Running for: N:{N}, M:{M}")
        try:
            scalable_df = getScalableDataFrame(M=M, N=N)
            interventionValue = 1; targetValue = 1
            start = tm.time()
            scalarProblem = ScalarProblem.buildScalarProblem(M=M, N=N, interventionValue=interventionValue, targetValue=targetValue, df=scalable_df, minimum = True)
            logger.info("MIN Problem Built")
            lower , lower_iterations = scalarProblem.solve()
            logger.info(f"Minimum Optimization N:{N}, M:{M}: Lower: {lower}, Iterations: {lower_iterations}")

            # logger.info("Building MAX Problem")
            # scalarProblem = ScalarProblem.buildScalarProblem(M=M, N=N, interventionValue=interventionValue, targetValue=targetValue, df=scalable_df, minimum = False)
            # upper, upper_iterations = scalarProblem.solve()
            upper_iterations = None
            # logger.info(f"Maximum Optimization N:{N}, M:{M}: Upper: {upper}, Iterations: {upper_iterations}")
            end = tm.time()
            upper = None
            total_time = end-start

            df = pd.read_csv("./outputs/ad_hoc_results.csv")
            new_row = {'N': N,'M': M,'LOWER_BOUND': lower,'LOWER_BOUND_REQUIRED_ITERATIONS': lower_iterations,'UPPER_BOUND': upper,'UPPER_BOUND_REQUIRED_ITERATIONS': upper_iterations, 'TOTAL_SECONDS_TAKEN':total_time}
        except Exception as e:
            logger.error(f"Error_N:{N}_M:{M}_: {e}")
            with open("./outputs/ad_hoc_error_log.txt", 'a') as file:
                file.write(f"Error: {e}")
            df = pd.read_csv("./outputs/ad_hoc_results.csv")
            new_row = {'N': N,'M': M,'LOWER_BOUND': None,'LOWER_BOUND_REQUIRED_ITERATIONS': None,'UPPER_BOUND': None,'UPPER_BOUND_REQUIRED_ITERATIONS': None, 'TOTAL_SECONDS_TAKEN':None}

        new_row_df = pd.DataFrame([new_row])
        df = pd.concat([df, new_row_df], ignore_index=True)
        df.to_csv("./outputs/ad_hoc_results.csv", index=False)
    logger.info("Done")

if __name__=="__main__":
    main()