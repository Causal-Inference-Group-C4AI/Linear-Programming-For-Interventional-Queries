from enum import Enum


# All the paths are from the project root directory
class DirectoriesPath(Enum):
    TEST_CASES_INPUTS = "causal_reasoning/test_cases/inputs"
    CSV_PATH = "causal_reasoning/data"


class Examples(Enum):
    CSV_ITAU_EXAMPLE = "causal_reasoning/data/itau.csv"
    TXT_ITAU_EXAMPLE = "causal_reasoning/test_cases/inputs/itau.txt"
    CSV_BALKE_PEARL_EXAMPLE = "causal_reasoning/data/balke_pearl.csv"
    TXT_BALKE_PEARL_EXAMPLE = "causal_reasoning/test_cases/inputs/balke_pearl.txt"
    CSV_2SCALING = "causal_reasoning/data/2_scaling_case.csv"
    CSV_N1M1="causal_reasoning/data/n1_m1_scaling_case.csv"
    CSV_N2M1="causal_reasoning/data/n2_m1_scaling_case.csv"
    CSV_N3M1="causal_reasoning/data/n3_m1_scaling_case.csv"
    CSV_N4M1="causal_reasoning/data/n4_m1_scaling_case.csv"
    CSV_N5M1="causal_reasoning/data/n5_m1_scaling_case.csv"    
    CSV_N1M2="causal_reasoning/data/n1_m2_scaling_case.csv"
    CSV_N2M2="causal_reasoning/data/n2_m2_scaling_case.csv"
    CSV_N3M2="causal_reasoning/data/n3_m2_scaling_case.csv"
    CSV_N4M2="causal_reasoning/data/n4_m2_scaling_case.csv"
    CSV_N5M2="causal_reasoning/data/n5_m2_scaling_case.csv"

