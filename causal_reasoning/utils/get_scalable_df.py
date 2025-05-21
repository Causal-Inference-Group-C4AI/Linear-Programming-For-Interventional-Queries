import pandas as pd
from causal_reasoning.utils._enum import Examples

def getScalableDataFrame(M: int, N: int):
    if (N == 1 and M == 1):
        scalable_csv_path = Examples.CSV_N1M1.value
    elif (N == 2 and M == 1):
        scalable_csv_path = Examples.CSV_N2M1.value
    elif (N == 3 and M == 1):
        scalable_csv_path = Examples.CSV_N3M1.value
    elif (N == 4 and M == 1):
        scalable_csv_path = Examples.CSV_N4M1.value
    elif (N == 5 and M == 1):
        scalable_csv_path = Examples.CSV_N5M1.value
    elif (N == 6 and M == 1): 
        scalable_csv_path = Examples.CSV_N6M1.value
    elif (N == 7 and M == 1): 
        scalable_csv_path = Examples.CSV_N7M1.value
    elif (N == 8 and M == 1): 
        scalable_csv_path = Examples.CSV_N8M1.value
    elif (N == 9 and M == 1): 
        scalable_csv_path = Examples.CSV_N9M1.value
    elif (N == 10 and M == 1):
        scalable_csv_path = Examples.CSV_N10M1.value
    elif (N == 1 and M == 2):
        scalable_csv_path = Examples.CSV_N1M2.value    
    elif (N == 2 and M == 2):
        scalable_csv_path = Examples.CSV_N2M2.value
    elif (N == 3 and M == 2):
        scalable_csv_path = Examples.CSV_N3M2.value
    elif (N == 4 and M == 2):
        scalable_csv_path = Examples.CSV_N4M2.value
    elif (N == 5 and M == 2):
        scalable_csv_path = Examples.CSV_N5M2.value
    elif (N == 1 and M == 3):
        scalable_csv_path = Examples.CSV_N1M3.value
    elif (N == 2 and M == 3):
        scalable_csv_path = Examples.CSV_N2M3.value
    elif (N == 3 and M == 3):
        scalable_csv_path = Examples.CSV_N3M3.value
    elif (N == 4 and M == 3):
        scalable_csv_path = Examples.CSV_N4M3.value
    elif (N == 5 and M == 3):
        scalable_csv_path = Examples.CSV_N5M3.value
    elif (N == 1 and M == 4):
        scalable_csv_path = Examples.CSV_N1M4.value
    elif (N == 2 and M == 4):
        scalable_csv_path = Examples.CSV_N2M4.value
    elif (N == 3 and M == 4):
        scalable_csv_path = Examples.CSV_N3M4.value
    elif (N == 4 and M == 4):
        scalable_csv_path = Examples.CSV_N4M4.value
    elif (N == 5 and M == 4):
        scalable_csv_path = Examples.CSV_N5M4.value

    return pd.read_csv(scalable_csv_path)