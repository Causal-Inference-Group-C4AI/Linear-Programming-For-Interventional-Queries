import pandas as pd

from causal_reasoning.graph.graph import Graph
from causal_reasoning.utils._enum import Examples
from causal_reasoning.causal_model import CausalModel
from causal_reasoning.causal_model import get_graph
from causal_reasoning.utils.probabilities_helper import ProbabilitiesHelper

def main():
    # balke_input = "Z -> X, X -> Y, U1 -> X, U1 -> Y, U2 -> Z"
    # balke_unobs = ["U1", "U2"]
    # balke_target = "Y"
    # balke_intervention = "X"    
    
    # P_BLAT_0 = ProbabilitiesHelper.find_probability(
    #     dataFrame=rca_df, 
    #     indexToLabel=graph.indexToLabel, 
    #     variableRealizations={graph.labelToIndex["MS-B_Latency"]: 0},
    #     v=False)
    
    # P_BLAT_1 = 1 - P_BLAT_0

    # P_OUT_1_BERROR_1_BLAT_0 = ProbabilitiesHelper.find_conditional_probability(
    #     dataFrame=rca_df,
    #     indexToLabel=graph.indexToLabel,
    #     targetRealization= {graph.labelToIndex["Outage"]: 1},
    #     conditionRealization= {graph.labelToIndex["MS-B_Error"]: 1, graph.labelToIndex["MS-B_Latency"]: 0},
    #     v=False,
    # )

    # P_OUT_1_BERROR_1_BLAT_1 = ProbabilitiesHelper.find_conditional_probability(
    #     dataFrame=rca_df,
    #     indexToLabel=graph.indexToLabel,
    #     targetRealization= {graph.labelToIndex["Outage"]: 1},
    #     conditionRealization= {graph.labelToIndex["MS-B_Error"]: 1, graph.labelToIndex["MS-B_Latency"]: 1},
    #     v=False,
    # )

    # query = P_BLAT_0 * P_OUT_1_BERROR_1_BLAT_0 + P_BLAT_1 * P_OUT_1_BERROR_1_BLAT_1
    # print(f"P(Outage=1|do(MSB-Error=1)) = {query}")

    # # ---------------------------------
    # print("----------------- \n -------------")
    # # AC = BL = 0:
    # P_OUT_1_AC_0_BE_1 = ProbabilitiesHelper.find_conditional_probability(
    #     dataFrame=rca_df,
    #     indexToLabel=graph.indexToLabel,
    #     targetRealization= {graph.labelToIndex["Outage"]: 1},
    #     conditionRealization= {graph.labelToIndex["MS-B_Error"]: 1, graph.labelToIndex["MS-A_Crash"]: 0},
    #     v=False,
    # )    

    # P_AC_0_BE_1_BL_0 = ProbabilitiesHelper.find_conditional_probability(
    #     dataFrame=rca_df,
    #     indexToLabel=graph.indexToLabel,
    #     targetRealization= {graph.labelToIndex["MS-A_Crash"]: 0},
    #     conditionRealization= {graph.labelToIndex["MS-B_Error"]: 1, graph.labelToIndex["MS-B_Latency"]: 0},
    #     v=False,
    # )    

    # P_BLAT_0 = ProbabilitiesHelper.find_probability(
    #     dataFrame=rca_df, 
    #     indexToLabel=graph.indexToLabel, 
    #     variableRealizations={graph.labelToIndex["MS-B_Latency"]: 0},
    #     v=False)

    # q1 = P_BLAT_0 * P_AC_0_BE_1_BL_0 * P_OUT_1_AC_0_BE_1
    
    # # AC = 0, BL = 1:
    # P_OUT_1_AC_0_BE_1 = ProbabilitiesHelper.find_conditional_probability(
    #     dataFrame=rca_df,
    #     indexToLabel=graph.indexToLabel,
    #     targetRealization= {graph.labelToIndex["Outage"]: 1},
    #     conditionRealization= {graph.labelToIndex["MS-B_Error"]: 1, graph.labelToIndex["MS-A_Crash"]: 0},
    #     v=False,
    # )    

    # P_AC_0_BE_1_BL_1 = ProbabilitiesHelper.find_conditional_probability(
    #     dataFrame=rca_df,
    #     indexToLabel=graph.indexToLabel,
    #     targetRealization= {graph.labelToIndex["MS-A_Crash"]: 0},
    #     conditionRealization= {graph.labelToIndex["MS-B_Error"]: 1, graph.labelToIndex["MS-B_Latency"]: 1},
    #     v=False,
    # )

    # P_BLAT_1 = 1 - P_BLAT_0
    
    # q2 = P_BLAT_1 * P_AC_0_BE_1_BL_1 * P_OUT_1_AC_0_BE_1

    # # AC = 1, BL = 0:
    # P_OUT_1_AC_1_BE_1 = ProbabilitiesHelper.find_conditional_probability(
    #     dataFrame=rca_df,
    #     indexToLabel=graph.indexToLabel,
    #     targetRealization= {graph.labelToIndex["Outage"]: 1},
    #     conditionRealization= {graph.labelToIndex["MS-B_Error"]: 1, graph.labelToIndex["MS-A_Crash"]: 1},
    #     v=False,
    # )    

    # P_AC_1_BE_1_BL_0 = ProbabilitiesHelper.find_conditional_probability(
    #     dataFrame=rca_df,
    #     indexToLabel=graph.indexToLabel,
    #     targetRealization= {graph.labelToIndex["MS-A_Crash"]: 1},
    #     conditionRealization= {graph.labelToIndex["MS-B_Error"]: 1, graph.labelToIndex["MS-B_Latency"]: 0},
    #     v=False,
    # )    

    # q3 = P_BLAT_0 * P_AC_1_BE_1_BL_0 * P_OUT_1_AC_1_BE_1

    # # AC = BL = 1:
    # P_AC_1_BE_1_BL_1 = ProbabilitiesHelper.find_conditional_probability(
    #     dataFrame=rca_df,
    #     indexToLabel=graph.indexToLabel,
    #     targetRealization= {graph.labelToIndex["MS-A_Crash"]: 1},
    #     conditionRealization= {graph.labelToIndex["MS-B_Error"]: 1, graph.labelToIndex["MS-B_Latency"]: 1},
    #     v=False,
    # )    

    # q4 = P_BLAT_1 * P_AC_1_BE_1_BL_1 * P_OUT_1_AC_1_BE_1

    # print(f"P(Outage=1|do(MS-B_ERROR=1) = {q1 + q2 + q3 + q4})")

    #---------------- Rodar com o algoritmo ----
    # graph: Graph = get_graph(file=Examples.TXT_RCA_EXAMPLE.value)
    
    rca_csv_path = Examples.CSV_RCA_EXAMPLE.value
    rca_df = pd.read_csv(rca_csv_path)    
    rca_unobs = ["Unob_helper_1", "Unob_helper_2", "Unob_helper_3", "Unob_helper_4", "Unob_helper_5",
                 "Unob_helper_6", "Unob_helper_7", "HeavyTraffic"]
    rca_intervention = "DB_Latency"
    rca_intervention_value = 1
    rca_target = "MS-A_Latency"
    rca_target_value = 1

    rca_edges = "DB_Change -> DB_Latency, DB_Latency -> MS-B_Latency, MS-B_Latency -> MS-B_Error, MS-B_Latency -> MS-A_Latency, MS-B_Error -> MS-A_Error, MS-A_Latency -> MS-A_Threads, MS-A_Threads -> MS-A_Crash, MS-A_Error -> Outage, MS-A_Crash -> Outage, HeavyTraffic -> DB_Latency, HeavyTraffic -> MS-A_Latency, Unob_helper_1 -> DB_Change, Unob_helper_2 -> MS-B_Latency, Unob_helper_3 -> MS-B_Error, Unob_helper_4 -> MS-A_Error, Unob_helper_5 -> MS-A_Threads, Unob_helper_6 -> MS-A_Crash, Unob_helper_7 -> Outage"

    rca_model = CausalModel(
        data=rca_df,
        edges=rca_edges,
        unobservables=rca_unobs,
        interventions=rca_intervention,
        interventions_value=rca_intervention_value,
        target=rca_target,
        target_value=rca_target_value,
    )
    rca_model.inference_query()

if __name__ == "__main__":
    main()
