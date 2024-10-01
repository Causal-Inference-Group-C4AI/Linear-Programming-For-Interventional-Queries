#include <bits/stdc++.h>
#include "cComponent.h"
#include "Logger.h"

using namespace std;

vector<vector<int>> adj; // 1-indexed!
vector<vector<int>> parents; // parents of each node (dual of adj).
map<string,int> labelToIndex; // Also 1-indexed.
map<int,string> indexToLabel; // debugging.
vector<int> cardinalities; // <= 1 implies unkown.
vector<bool> visited;
int currComponent = 0;
vector<int> currNodes;
vector<cComponent> dagComponents;

void dfs(int node) {
    visited[node] = true;
    currNodes.push_back(node);
    bool isObservable = cardinalities[node] > 1;
    
    if (!isObservable) {
        for (int adjNode: adj[node]) {
            if (!visited[adjNode]) dfs(adjNode);            
        }    
    } else {
        for (int parentNode: parents[node]) {
            if (!visited[parentNode] && cardinalities[parentNode] < 1) dfs(parentNode);
        }    
    }       
}

// Solves a relaxed problem for each c-component (sharp if the c-component has only one latent variable)
void boundForCanonicalPartitions() {
    for (int i = 0; i < dagComponents.size(); i++) {
        int64_t canonicalPartition = 1;
        for (int node: dagComponents[i].nodes) {            
            if (cardinalities[node] > 1) {
                int64_t base = cardinalities[node];
                int64_t exponent = 1;
                for (int parent: parents[node]) {
                    if (cardinalities[parent] > 1) {
                        exponent *= cardinalities[parent];
                    }
                }
                canonicalPartition *= pow(base, exponent);
            }            
        }
        cout << "For the c-component #" << i + 1 << " the equivalente canonical partition = " << canonicalPartition << endl;
    }
}

int main() {    
    int numNodes, numEdges; cin >> numNodes >> numEdges;    
    adj.resize(numNodes + 1); cardinalities.resize(numNodes + 1);    
    visited.resize(numNodes + 1, false); parents.resize(numNodes + 1);

    string label; int cardinality;
    for (int i = 1; i <= numNodes; i++) {
        cin >> label >> cardinality;
        labelToIndex[label] = i; indexToLabel[i] = label;
        cardinalities[i] = cardinality;
    }

    // causal L to R (u -> v).
    string u, v;
    int currIndex = 1;    
    for (int i = 0; i < numEdges; i++) {        
        cin >> u >> v; vector<int> indexesUV;        
        
        for (string str: {u, v}) indexesUV.push_back(labelToIndex[str]);                       
        
        adj[indexesUV[0]].push_back(indexesUV[1]);                
        parents[indexesUV[1]].push_back(indexesUV[0]);
    }    

    Logger::fullLog(numNodes, &indexToLabel, &labelToIndex, &cardinalities, &adj, &dagComponents);    

    for (int i = 1; i <= numNodes; i++) {
        if (!visited[i] && cardinalities[i] < 1) {
            currNodes.clear();
            dfs(i);
            dagComponents.push_back(cComponent(currNodes));
            currComponent++;
        }
    }
    
    for (int i = 0; i < dagComponents.size(); i++) {
        cout << "c-component #" << i + 1 << endl;

        for (int el: dagComponents[i].nodes) {
            cout << "node " << el << " (" << indexToLabel[el] << ") - " << (cardinalities[el] < 1 ? "Latent" : "Observable") << endl;
        }
    }

    boundForCanonicalPartitions();
    
    return 0;
}