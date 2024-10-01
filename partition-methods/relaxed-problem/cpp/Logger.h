#ifndef LOGGER_H
#define LOGGER_H

using namespace std;

#include <iostream>
#include <vector>
#include <map>
#include <string>
#include "cComponent.h"

class Logger {
public:
    static void fullLog(int numNodes, map<int,string>* indexToLabel, map<string,int>* labelToIndex, vector<int>* cardinalities,  vector<vector<int>>* adj, vector<cComponent>* dagComponents);        

    static void debugIndexToLabel(int numNodes, map<int,string>* indexToLabel);

    static void debugLabelToIndex(int numNodes, map<string,int>* labelToIndex);

    static void debugLatent(int numNodes, vector<int>* cardinalities, map<int,string>* indexToLabel);
    
    static void debugGraph(int numNodes, map<int,string>* indexToLabel, vector<vector<int>>* adj);
    
    static void printCComponents(vector<cComponent>* dagComponents, int numNodes, map<int,string>* indexToLabel, vector<vector<int>>* adj, vector<int>* cardinalities);
};

#endif