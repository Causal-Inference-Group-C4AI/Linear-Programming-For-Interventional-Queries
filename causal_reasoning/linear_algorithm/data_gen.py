import random
import pandas as pd


def f(a: int, b: int):
    return 1 if random.randrange(100) < 5 else a ^ b

def fx(u: int):
    return int(not u) if random.randrange(100) < 2 else u

def generate_data_for_scale_case(n_variables: int, samples: int = 10000):    
    U = [random.choice([0, 1]) for _ in range(samples)]
    X = [fx(u) for u in U]

    B = []
    A = []

    B1 = [f(X[i], U[i]) for i in range(samples)]
    A1 = [f(B1[i], U[i]) for i in range(samples)]
    B.append(B1)
    A.append(A1)

    # For column output
    columns_values = {
        'U': U,
        'X': X,
        'B1': B1,
        'A1': A1
    }

    for i in range(1, n_variables):
        Bi = [f(A[i - 1][j], U[j]) for j in range(samples)]
        Ai = [f(Bi[j], U[j]) for j in range(samples)]
        B.append(Bi)
        A.append(Ai)
        columns_values[f'B{i + 1}'] = Bi
        columns_values[f'A{i + 1}'] = Ai

    last_A = A[-1]
    Y = [f(last_A[j], U[j]) for j in range(samples)]
    columns_values['Y'] = Y

    df = pd.DataFrame(columns_values)
    df.to_csv(f"{n_variables}_scaling_case.csv", index=False)

if __name__ == "__main__":
    for i in range(1, 20):
        generate_data_for_scale_case(i)
