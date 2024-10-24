# Canonical-Partition
Códigos para estimar as partições canônicas de DAGs. Este repositório é privado porque lida com um problema em aberto e portanto é possível que parte dos algoritmos usados/desenvolvidos sejam originais. Além disso, podem conter partes de códigos proprietários.

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

