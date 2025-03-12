# Canonical-Partition
 Códigos para estimar as partições canônicas de DAGs. Este repositório é privado porque lida com um problema em aberto e portanto é possível que parte dos algoritmos usados/desenvolvidos sejam originais. Além disso, podem conter partes de códigos proprietários.

## Boas Práticas de Eng. de Software

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



## Relaxed problem:
Determina cada confounded component (c-component) e monta um DAG equivalente. Nele, cada c-component contém apenas uma variável latente, cuja cardinalidade é determinada de forma exata. O problema resultante é menos restringido, e portanto o bound para cada query contém o bound que seria considerado sharp.

### Input:
O número de vérticos do DAG seguido pelo número de arestas. Em seguida, o label de cada variável seguido de sua cardinalidade - se latente colocar 0. Por fim, deve-se especificar cada uma das arestas, o que é feito colocando o label das duas variáveis envolvidas. A interpretação é que a variável da esquerda causa a da direita.

### Como executar:
**(cpp)**:
- Primeiro, entre na pasta em que se encontra o código fonte.
```bash
cd partition-methods/relaxed-problem/cpp
```
- Em seguida, compile o programa com:
```bash
g++ estimateCanonical.cpp Logger.cpp -o yourExecutableName
```
- Por fim, rode com:
```bash
./yourExecutableName
```

**(python)**:
- Rode o programa com:
```bash
python3 -m partition_methods.relaxed_problem.python.canonicalPartitions
```
O "-m" é necessário para executarmos como módulo, caso contrário o programa não consegue realizar os imports corretamente.
Você pode montar seu próprio input ou usar os que já estão prontos na pasta test-cases/inputs.

## Generator:
- Ainda está sendo feito.

### Como executar:
É necessário adicionar o root do projeto ao seu .bashrc para que os imports entre arquivos funcionem. Abra o arquivo com o editor de sua escolha:
```shell
nano ~/.bashrc
```

E adicione a linha abaixo ao arquivo, substituindo o caminho por como está em sua máquina.
```shell
export PYTHONPATH=$PYTHONPATH:/home/path/to/Canonical-Partition/
```

