# Canonical-Partition
Códigos para estimar as partições canônicas de DAGs. Este repositório é privado porque lida com um problema em aberto e portanto é possível que parte dos algoritmos usados/desenvolvidos sejam originais. Além disso, podem conter partes de códigos proprietários.

## Relaxed problem:
Determina cada confounded component (c-component) e monta um DAG equivalente. Nele, cada c-component contém apenas uma variável latente, cuja cardinalidade é determinada de forma exata. O problema resultante é menos restringido, e portanto o bound para cada query contém o bound que seria considerado sharp.

### Input:
O número de vérticos do DAG seguido pelo número de arestas. Em seguida, o label de cada variável seguido de sua cardinalidade - se latente colocar 0. Por fim, deve-se especificar cada uma das arestas, o que é feito colocando o label das duas variáveis envolvidas. A interpretação é que a variável da esquerda causa a da direita.