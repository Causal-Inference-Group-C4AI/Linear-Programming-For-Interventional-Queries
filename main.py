from causal_usp_icti.utils.parser import parse_default_input, parse_file
from causal_usp_icti.utils._enum import Examples
from causal_usp_icti.linear_algorithm.opt_problem_builder import OptProblemBuilder

def main():
    graph_input = "Z -> X, X -> Y, U1 -> X, U1 -> Y, U2 -> Z"
    unobservables = ["U1", "U2"]
    target = "Y"
    intervention = "X"
    input_path = Examples.TXT_BALKE_PEARL_EXAMPLE.value
    csv_path = Examples.CSV_BALKE_PEARL_EXAMPLE.value

    print('---STR---')
    print(parse_default_input(graph_input, unobservables))
    print()
    print('---FILE---')
    print(parse_file(input_path))

    print('------')
    print('------')
    problem_builder= OptProblemBuilder()
    # TODO: BUILDER LINEAR PROBLEM: RECEIVE PATH OR THE STRINGS 
    problem_builder.get_query(str_graph=graph_input, unobservables=unobservables, intervention=intervention, intervention_value=1, target=target, target_value=1, csv_path=csv_path)

if __name__ == '__main__':
    main()
