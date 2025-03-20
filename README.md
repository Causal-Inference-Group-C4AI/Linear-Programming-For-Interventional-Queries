# Canonical-Partition (WIP)

## Relaxed problem:
Determina cada confounded component (c-component) e monta um DAG equivalente. Nele, cada c-component contém apenas uma variável latente, cuja cardinalidade é determinada de forma exata. O problema resultante é menos restringido, e portanto o bound para cada query contém o bound que seria considerado sharp.

## Boas Práticas de Eng. de Software

<a name="flake8"></a>
### Flake8 
**Flake8** is a powerful tool for enforcing style guidelines. It scans your code to identify deviations from PEP 8, such as improper indentation, excessive line lengths, and unused imports. By integrating Flake8 into your development workflow, you can maintain clean and consistent code, making it easier to read and maintain.

Key Features:
- **Syntax Checking:** Detects syntax errors that could cause your code to fail.
- **Style Enforcement:** Ensures adherence to PEP 8 guidelines, promoting uniform coding practices.
- **Plugin Support:** Extensible with plugins to add more checks or customize existing ones.

Usage Example:

```shell
flake8 your_script.py
```

Running this command will output any style violations or errors found in `your_script.py`, allowing you to address them promptly.

<br>

### Imports

#### Isort
**isort** focuses specifically on the organization of import statements. It automatically sorts imports alphabetically and separates them into sections (standard library, third-party, and local imports), ensuring that your import statements are both orderly and compliant with best practices. This not only enhances readability but also helps prevent merge conflicts and import-related errors.

Key Features:
- **Automatic Sorting:** Organizes imports alphabetically and by category.
- **Customization:** Allows configuration to match specific project requirements.

Usage Example:

isort is very easy to use. You can sort the imports in a Python file by running the following command in your terminal:

```shell
isort your_script.py
```

Or for all files:
```shell
isort .
```

After running the command, save the file to apply the sorted imports.

**Example of isort in Action:**

_Before isort:_
```python
import os
import sys
import requests
from mymodule import myfunction
import numpy as np
```

_After isort:_

```python
import os
import sys

import numpy as np
import requests

from mymodule import myfunction
```

In this example, isort has organized the imports into three distinct sections:
- **Standard Library Imports:** os, sys
- **Third-Party Imports:** numpy, requests
- **Local Application Imports:** mymodule

This separation improves readability and maintainability of your code by clearly distinguishing between different types of dependencies.

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
poetry run python causal_usp_icti/example/scipy_example.py
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
