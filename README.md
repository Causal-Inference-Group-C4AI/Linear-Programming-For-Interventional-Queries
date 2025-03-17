# Canonical-Partition (WIP)

## Install
### Linux
We're using [poetry](https://python-poetry.org/docs/) as pyhton dependency management.

- Activate poetry virtual environment
```bash
poetry shell
```
- Install dependencies
```bash
poetry install
```

## How to run
### Linux
- Activate poetry virtual environment
```bash
poetry shell
```

```bash
poetry run python script.py
```

Example:
```bash
poetry run python causal_usp_icti/scipy_example.py
```
The output should be:
```
Using the complete objective function, the results are:
Lower bound: -0.23 - Upper bound: -0.15

Using the complete objective function, the result for the positive query is:
Lower bound: 0.45 - Upper bound: 0.52
Using the complete objective function, the result for the negative query is:
Lower bound: 0.67 - Upper bound: 0.68

With the first method, we obtain the interval: [-0.23,-0.15]
With the second method, we obtain the interval: [-0.23,-0.15]
```

- To exit the poetry virtual environment run:

```bash
exit
```
or

```bash
deactivate
```