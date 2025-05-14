import pandas as pd

from causal_reasoning.utils._enum import Examples

itau_csv_path = Examples.CSV_ITAU_EXAMPLE.value
df = pd.read_csv(itau_csv_path)

countD0 = df[(df["D"] == 0)].shape[0]
countAll = df[(df["X"] == 0) & (df["Y"] == 0) & (df["D"] == 0)].shape[0]

print(f"Prob = {countAll / countD0}")