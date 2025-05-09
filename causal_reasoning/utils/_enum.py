from enum import Enum


# All the paths are from the project root directory
class DirectoriesPath(Enum):
    TEST_CASES_INPUTS = "causal_reasoning/test_cases/inputs"
    CSV_PATH = "causal_reasoning/data"


class Examples(Enum):
    CSV_ITAU_EXAMPLE = "causal_reasoning/data/itau.csv"
    TXT_ITAU_EXAMPLE = "causal_reasoning/test_cases/inputs/itau.txt"
    TXT_RCA_EXAMPLE = "causal_reasoning/test_cases/inputs/rca.txt"
    CSV_BALKE_PEARL_EXAMPLE = "causal_reasoning/data/balke_pearl.csv"
    CSV_RCA_EXAMPLE = "causal_reasoning/data/rca_without_latent.csv"
    TXT_BALKE_PEARL_EXAMPLE = "causal_reasoning/test_cases/inputs/balke_pearl.txt"
