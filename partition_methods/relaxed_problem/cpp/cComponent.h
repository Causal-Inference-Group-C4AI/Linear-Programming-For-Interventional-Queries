// cComponent.h
#ifndef CCOMPONENT_H
#define CCOMPONENT_H

#include <vector>

class cComponent {
public:
    std::vector<int> nodes; 

    cComponent() = default;
    
    cComponent(const std::vector<int>& nodesInit) 
        : nodes(nodesInit) {}
};

#endif
