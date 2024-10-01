#include <bits/stdc++.h>

using namespace std;

#include "cComponent.h"
#include "Logger.h"

void Logger::fullLog(int numNodes, map<int, string> *indexToLabel, map<string, int> *labelToIndex, vector<int> *cardinalities, vector<vector<int>> *adj, vector<cComponent> *dagComponents)
{
    debugIndexToLabel(numNodes, indexToLabel);
    debugLabelToIndex(numNodes, labelToIndex);
    debugLatent(numNodes, cardinalities, indexToLabel);
    debugGraph(numNodes, indexToLabel, adj);
    printCComponents(dagComponents, numNodes, indexToLabel, adj, cardinalities);
}

void Logger::debugIndexToLabel(int numNodes, map<int, string> *indexToLabel)
{
    cout << "debug indexToLabel" << endl;
    for (auto el : *indexToLabel)
    {
        cout << "index " << el.first << " label " << el.second << endl;
    }
}

void Logger::debugLabelToIndex(int numNodes, map<string, int> *labelToIndex)
{
    cout << "debug labelToIndex" << endl;
    for (auto el : *labelToIndex)
    {
        cout << "label " << el.first << " index " << el.second << endl;
    }
}

void Logger::debugLatent(int numNodes, vector<int> *cardinalities, map<int, string> *indexToLabel)
{
    cout << "Latent variables: \n"
         << endl;
    for (int i = 1; i <= numNodes; i++)
    {
        if ((*cardinalities)[i] < 1)
            cout << "latent var " << i << " with label " << (*indexToLabel)[i] << endl;
    }
}

void Logger::debugGraph(int numNodes, map<int, string> *indexToLabel, vector<vector<int>> *adj)
{
    cout << "debugging graph:\n"
         << endl;
    for (int i = 1; i <= numNodes; i++)
    {
        cout << "Edges from " << (*indexToLabel)[i] << endl;
        for (auto el : (*adj)[i])
        {
            cout << (*indexToLabel)[el] << " ";
        }
        cout << endl;
    }
}

void Logger::printCComponents(vector<cComponent> *dagComponents, int numNodes, map<int, string> *indexToLabel, vector<vector<int>> *adj, vector<int> *cardinalities)
{
    for (int i = 0; i < (*dagComponents).size(); i++)
    {
        cout << "c-component #" << i + 1 << endl;
        for (int el : (*dagComponents)[i].nodes)
        {
            cout << "node " << el << "(" << (*indexToLabel)[el] << ") - " << ((*cardinalities)[el] < 1 ? "Latent" : "Observable") << endl;
        }
    }
}
